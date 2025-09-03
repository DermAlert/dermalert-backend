from rest_framework import serializers
from .models import ConsentTerm, ConsentSignature, ConsentSignatureImage


class ConsentSignatureImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentSignatureImage
        fields = ["id", "image", "page_number"]
        read_only_fields = ["id"]


class ConsentTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentTerm
        fields = ["id", "version", "url", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConsentSignatureSerializer(serializers.ModelSerializer):
    images = ConsentSignatureImageSerializer(many=True, read_only=True)

    class Meta:
        model = ConsentSignature
        fields = [
            "id",
            "term",
            "user",
            "has_signed",
            "signed_at",
            "images",
        ]
        read_only_fields = ["id", "user", "signed_at"]


class ConsentSignatureCreateSerializer(serializers.ModelSerializer):
    # upload múltiplas imagens via lista
    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False),
        allow_empty=False,
        write_only=True,
        required=True,
    )

    class Meta:
        model = ConsentSignature
        fields = ["term", "has_signed", "images"]

    def create(self, validated_data):
        images = validated_data.pop("images")
        signature = ConsentSignature.objects.create(**validated_data)
        # create images
        objs = [
            ConsentSignatureImage(signature=signature, image=img, page_number=i + 1)
            for i, img in enumerate(images)
        ]
        ConsentSignatureImage.objects.bulk_create(objs)
        return signature
