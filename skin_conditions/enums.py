from django.db import models


class BodySite(models.TextChoices):
    # Head & neck
    SCALP = "head_neck.scalp", "Scalp"
    FOREHEAD = "head_neck.forehead", "Forehead"
    EYES = "head_neck.eyes", "Eyes"
    NOSE = "head_neck.nose", "Nose"
    MOUTH = "head_neck.mouth", "Mouth"
    EARS = "head_neck.ears", "Ears"
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
    # Extremities with laterality
    SHOULDER_RIGHT = "extremities.shoulder_right", "Right shoulder"
    SHOULDER_LEFT = "extremities.shoulder_left", "Left shoulder"
    ARM_RIGHT = "extremities.arm_right", "Right arm"
    ARM_LEFT = "extremities.arm_left", "Left arm"
    FOREARM_RIGHT = "extremities.forearm_right", "Right forearm"
    FOREARM_LEFT = "extremities.forearm_left", "Left forearm"
    HAND_RIGHT = "extremities.hand_right", "Right hand"
    HAND_LEFT = "extremities.hand_left", "Left hand"
    THIGH_RIGHT = "extremities.thigh_right", "Right thigh"
    THIGH_LEFT = "extremities.thigh_left", "Left thigh"
    LEG_RIGHT = "extremities.leg_right", "Right leg"
    LEG_LEFT = "extremities.leg_left", "Left leg"
    FOOT_RIGHT = "extremities.foot_right", "Right foot"
    FOOT_LEFT = "extremities.foot_left", "Left foot"


class SkinConditionType(models.TextChoices):
    CANCER = "cancer", "Cancer"
    WOUND = "wound", "Wound"
