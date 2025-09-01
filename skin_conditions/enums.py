from django.db import models


class BodySite(models.TextChoices):
    # Head & neck
    SCALP = "head_neck.scalp", "Scalp"
    FACE = "head_neck.face", "Face"
    NECK = "head_neck.neck", "Neck"
    # Trunk
    CHEST_ANT = "trunk.chest_front", "Chest (anterior)"
    CHEST_POST = "trunk.chest_back", "Chest (posterior)"
    UPPER_ABD = "trunk.upper_abdomen", "Upper abdomen"
    LOWER_ABD = "trunk.lower_abdomen", "Lower abdomen"
    BACK = "trunk.back", "Back"
    FLANKS = "trunk.flanks", "Flanks"
    # Pelvic
    PUBIS = "pelvis.pubis", "Pubis"
    GENITALS = "pelvis.genitals", "Genitals"
    BUTTOCKS = "pelvis.buttocks", "Buttocks"
    COCCYX = "pelvis.coccyx", "Coccyx"
    # Extremities (without laterality here)
    SHOULDER = "extremities.shoulder", "Shoulder"
    ARM = "extremities.arm", "Arm"
    FOREARM = "extremities.forearm", "Forearm"
    HAND = "extremities.hand", "Hand"
    THIGH = "extremities.thigh", "Thigh"
    LEG = "extremities.leg", "Leg"
    FOOT = "extremities.foot", "Foot"

class SkinConditionType(models.TextChoices):
    CANCER = "cancer", "Cancer"
    WOUND = "wound", "Wound"