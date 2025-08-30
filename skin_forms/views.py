from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from skin_forms.models import Wound
from skin_forms.models.image import Image
from skin_forms.serializers import WoundSerializer, ImageSerializer
from django.contrib.contenttypes.models import ContentType


class WoundViewSet(
	mixins.ListModelMixin,
	mixins.RetrieveModelMixin,
	mixins.CreateModelMixin,
	mixins.UpdateModelMixin,
	viewsets.GenericViewSet,
):
	queryset = Wound.objects.filter(is_deleted=False).order_by("-created_at")
	serializer_class = WoundSerializer

	@action(detail=True, methods=["post"], url_path="upload-images")
	def upload_images(self, request, pk=None):
		wound = self.get_object()
		files = request.FILES.getlist("images") or []
		image_type = request.data.get("image_type") or Image._meta.get_field("image_type").get_default()
		created = []
		ct = ContentType.objects.get_for_model(Wound)
		for f in files:
			obj = Image.objects.create(
				content_type=ct, object_id=wound.id, image=f, image_type=image_type
			)
			created.append(obj)
		return Response(
			ImageSerializer(created, many=True, context=self.get_serializer_context()).data,
			status=status.HTTP_201_CREATED,
		)

	def perform_create(self, serializer):
		user = getattr(self.request, "user", None)
		if user is None or not getattr(user, "is_authenticated", False):
			user = None
		serializer.save(created_by=user, updated_by=user)

	def perform_update(self, serializer):
		user = getattr(self.request, "user", None)
		if user is None or not getattr(user, "is_authenticated", False):
			user = None
		serializer.save(updated_by=user)


class ImageViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
	queryset = Image.objects.all().order_by("-created_at")
	serializer_class = ImageSerializer

