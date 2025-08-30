from typing import List

from rest_framework import serializers

from skin_forms.models import Wound
from skin_forms.models.image import Image
from django.contrib.contenttypes.models import ContentType
from skin_forms.enums.image import ImageType


class ImageSerializer(serializers.ModelSerializer):
	image = serializers.ImageField()

	class Meta:
		model = Image
		fields = ["id", "image", "image_type", "created_at"]
		read_only_fields = ["id", "created_at"]


class WoundSerializer(serializers.ModelSerializer):
	# Write-only list of images for creation/update
	images = serializers.ListField(
		child=serializers.ImageField(), write_only=True, required=False
	)
	image_type = serializers.ChoiceField(
		choices=ImageType.choices, required=False, write_only=True
	)

	# Read-only nested images
	attachments = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = Wound
		fields = [
			"id",
			# measures
			"height_mm",
			"width_mm",
			# characteristics
			"wound_edges",
			"wound_bed_tissue",
			"depth_of_tissue_injury",
			"exudate_type",
			# infection signs
			"increased_pain",
			"perilesional_erythema",
			"perilesional_edema",
			"heat_or_warm_skin",
			"increased_exudate",
			"purulent_exudate",
			"friable_tissue",
			"stagnant_wound",
			"biofilm_compatible_tissue",
			"odor",
			"hypergranulation",
			"wound_size_increase",
			"satallite_lesions",
			"grayish_wound_bed",
			# computed
			"total_score",
			# misc
			"notes",
			# upload helpers
			"images",
			"image_type",
			# output
			"attachments",
		]
		read_only_fields = ["id", "total_score", "attachments"]

	def create(self, validated_data):
		# Safely extract images from validated_data or request.FILES
		raw_images = validated_data.pop("images", None)
		image_type = validated_data.pop("image_type", ImageType.DERMOSCOPIC)
		images: List = []
		if raw_images is not None:
			if isinstance(raw_images, (list, tuple)):
				images = list(raw_images)
			else:
				images = [raw_images]
		# Prefer files from request for multipart submissions
		request = self.context.get("request")
		if request is not None:
			files = request.FILES.getlist("images")
			if files:
				images = list(files)
		wound: Wound = super().create(validated_data)
		ct = ContentType.objects.get_for_model(Wound)
		for img in images:
			Image.objects.create(
				content_type=ct, object_id=wound.id, image=img, image_type=image_type
			)
		return wound

	def update(self, instance, validated_data):
		# Optional support to upload more images when updating
		raw_images = validated_data.pop("images", None)
		image_type = validated_data.pop("image_type", ImageType.DERMOSCOPIC)
		images: List = []
		if raw_images is not None:
			if isinstance(raw_images, (list, tuple)):
				images = list(raw_images)
			else:
				images = [raw_images]
		request = self.context.get("request")
		if request is not None:
			files = request.FILES.getlist("images")
			if files:
				images = list(files)
		instance = super().update(instance, validated_data)
		ct = ContentType.objects.get_for_model(Wound)
		for img in images:
			Image.objects.create(
				content_type=ct, object_id=instance.id, image=img, image_type=image_type
			)
		return instance

	def get_attachments(self, obj: Wound):
		ct = ContentType.objects.get_for_model(Wound)
		qs = Image.objects.filter(content_type=ct, object_id=obj.id).order_by(
			"-created_at"
		)
		return ImageSerializer(qs, many=True, context=self.context).data

