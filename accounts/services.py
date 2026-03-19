import hashlib
import secrets
from datetime import datetime, time, timedelta
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.exceptions import ValidationError

from accounts.models import InviteWork, Work
from accounts.validators import normalize_cpf, validate_cpf

User = get_user_model()


def build_client_url(template: str, **kwargs) -> str:
    escaped_kwargs = {
        key: quote(str(value), safe="") for key, value in kwargs.items()
    }
    return template.format(**escaped_kwargs)


def send_html_email(to_email: str, subject: str, text_body: str, html_body: str) -> None:
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=False)


def send_registration_invite_email(invite: InviteWork, raw_token: str) -> str:
    invite_url = build_client_url(
        settings.REGISTRATION_INVITE_URL_TEMPLATE,
        token=raw_token,
    )
    subject = "Convite para completar seu cadastro"
    text_body = (
        "Voce foi convidado para acessar o DermAlert. "
        f"Conclua seu cadastro em: {invite_url}"
    )
    html_body = (
        "<p>Voce foi convidado para acessar o DermAlert.</p>"
        f"<p><a href=\"{invite_url}\">Concluir cadastro</a></p>"
        "<p>Este link expira em 24 horas.</p>"
    )
    send_html_email(invite.email, subject, text_body, html_body)
    return invite_url


def send_password_reset_email(user) -> tuple[str, str, str]:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = build_client_url(
        settings.PASSWORD_RESET_URL_TEMPLATE,
        uid=uid,
        token=token,
    )
    subject = "Redefinicao de senha"
    text_body = (
        "Recebemos uma solicitacao para redefinir sua senha. "
        f"Use este link: {reset_url}"
    )
    html_body = (
        "<p>Recebemos uma solicitacao para redefinir sua senha.</p>"
        f"<p><a href=\"{reset_url}\">Redefinir senha</a></p>"
        "<p>Se voce nao solicitou esta alteracao, ignore este email.</p>"
    )
    send_html_email(user.email, subject, text_body, html_body)
    return uid, token, reset_url


def send_unit_assignment_email(user, health_unit, permission_role: str) -> None:
    subject = "Inclusao confirmada em unidade de saude"
    text_body = (
        f"Seu acesso ao DermAlert foi vinculado a unidade {health_unit.name} "
        f"com o perfil {permission_role}."
    )
    html_body = (
        f"<p>Seu acesso ao DermAlert foi vinculado a unidade "
        f"<strong>{health_unit.name}</strong> com o perfil "
        f"<strong>{permission_role}</strong>.</p>"
    )
    send_html_email(user.email, subject, text_body, html_body)


def resolve_user_by_identity(*, cpf: str, email: str, exclude_user=None):
    cpf = normalize_cpf(cpf)
    email = (email or "").strip().lower()

    queryset = User.objects.all()
    if exclude_user is not None:
        queryset = queryset.exclude(pk=exclude_user.pk)

    cpf_user = queryset.filter(cpf=cpf).first() if cpf else None
    email_user = (
        queryset.filter(email__iexact=email).exclude(email="").first()
        if email
        else None
    )

    if cpf_user and email_user and cpf_user.pk != email_user.pk:
        raise ValidationError(
            {"detail": "CPF and email belong to different users."}
        )

    return cpf_user or email_user


def coerce_date_to_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        if timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value
    coerced = datetime.combine(value, time.min)
    return timezone.make_aware(coerced, timezone.get_current_timezone())


def get_invite_from_token(raw_token: str):
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    return (
        InviteWork.objects.select_related("user", "health_unit_code")
        .filter(hash=token_hash, is_deleted=False)
        .first()
    )


def create_registration_invite(
    *,
    user,
    name: str,
    cpf: str,
    email: str,
    health_unit,
    permission_role: str,
    start_date,
    end_date,
    created_by,
):
    InviteWork.objects.filter(
        user=user,
        health_unit_code=health_unit,
        is_deleted=False,
    ).update(is_active=False, is_deleted=True)

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    invite = InviteWork.objects.create(
        hash=token_hash,
        user=user,
        name=name,
        cpf=normalize_cpf(cpf),
        email=email,
        permission_role=permission_role,
        health_unit_code=health_unit,
        expires_at=timezone.now() + timedelta(hours=24),
        start_date_work=coerce_date_to_datetime(start_date),
        end_date_work=coerce_date_to_datetime(end_date),
        created_by=created_by,
        updated_by=created_by,
    )
    send_registration_invite_email(invite, raw_token)
    return invite


@transaction.atomic
def assign_professional_to_health_unit(
    *,
    name: str,
    cpf: str,
    email: str,
    health_unit,
    permission_role: str,
    start_date,
    end_date=None,
    created_by,
):
    cpf = validate_cpf(cpf)
    email = (email or "").strip().lower()

    user = resolve_user_by_identity(cpf=cpf, email=email)

    if user is None:
        user = User(
            cpf=cpf,
            email=email,
            name=name,
            is_active=False,
        )
        user.set_unusable_password()
        user.save()
    else:
        user.cpf = cpf
        user.email = email
        user.name = name
        user.updated_by = created_by
        user.save()

    work = Work.objects.filter(user=user, health_unit=health_unit).first()

    if work and not work.is_deleted and work.is_active and user.has_usable_password():
        raise ValidationError(
            {"detail": "Professional is already linked to this health unit."}
        )

    if work is None:
        work = Work(
            user=user,
            health_unit=health_unit,
            created_by=created_by,
        )

    work.permission_role = permission_role
    work.start_date = start_date
    work.end_date = end_date
    work.updated_by = created_by

    if user.has_usable_password() and user.is_active:
        work.is_active = True
        work.is_deleted = False
        work.full_clean()
        work.save()
        send_unit_assignment_email(user, health_unit, permission_role)
        return work, "linked"

    work.is_active = False
    work.is_deleted = False
    work.full_clean()
    work.save()

    create_registration_invite(
        user=user,
        name=name,
        cpf=cpf,
        email=email,
        health_unit=health_unit,
        permission_role=permission_role,
        start_date=start_date,
        end_date=end_date,
        created_by=created_by,
    )
    return work, "invited"


@transaction.atomic
def complete_registration_invite(*, raw_token: str, password: str):
    invite = get_invite_from_token(raw_token)

    if invite is None or invite.is_deleted or not invite.is_active:
        raise ValidationError({"detail": "Invite token is invalid."})

    if invite.accepted_at is not None:
        raise ValidationError({"detail": "Invite token has already been used."})

    if invite.expires_at and invite.expires_at < timezone.now():
        raise ValidationError({"detail": "Invite token has expired."})

    user = invite.user or resolve_user_by_identity(cpf=invite.cpf, email=invite.email)
    if user is None:
        user = User.objects.create_user(
            cpf=invite.cpf,
            password=password,
            email=invite.email,
            name=invite.name,
            is_active=True,
        )
    else:
        if user.has_usable_password() and user.is_active:
            raise ValidationError({"detail": "User has already completed registration."})

        user.cpf = invite.cpf
        user.email = invite.email
        user.name = invite.name
        user.is_active = True
        user.set_password(password)
        user.save()

    work, _ = Work.objects.get_or_create(
        user=user,
        health_unit=invite.health_unit_code,
        defaults={
            "created_by": invite.created_by,
        },
    )
    work.permission_role = invite.permission_role
    work.start_date = (
        invite.start_date_work.date()
        if invite.start_date_work
        else timezone.localdate()
    )
    work.end_date = invite.end_date_work.date() if invite.end_date_work else None
    work.is_active = True
    work.is_deleted = False
    work.updated_by = invite.updated_by or invite.created_by
    work.full_clean()
    work.save()

    invite.accepted_at = timezone.now()
    invite.is_active = False
    invite.is_deleted = True
    invite.updated_by = user
    invite.user = user
    invite.save(update_fields=["accepted_at", "is_active", "is_deleted", "updated_by", "user"])

    return invite, user, work
