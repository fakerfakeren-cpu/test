package com.astralfall.client.model;

import com.astralfall.client.render.States;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

public class StalkerModel extends EntityModel<States.Stalker> {
    private final ModelPart body, head, leftArm, rightArm, leftLeg, rightLeg, cape;

    public StalkerModel(ModelPart root) {
        super(root);
        body = root.getChild("body");
        head = body.getChild("head");
        leftArm = body.getChild("left_arm");
        rightArm = body.getChild("right_arm");
        cape = body.getChild("cape");
        leftLeg = root.getChild("left_leg");
        rightLeg = root.getChild("right_leg");
    }

    @Override
    public void setupAnim(States.Stalker s) {
        super.setupAnim(s);
        float t = s.ageInTicks;
        float walk = s.walkAnimationPos;
        float speed = Math.min(1f, s.walkAnimationSpeed);
        head.yRot = s.yRot * Mth.DEG_TO_RAD;
        head.xRot = s.xRot * Mth.DEG_TO_RAD - 0.15f;
        if (s.frozen) {
            // statue-still, reaching, with the occasional wrong-looking twitch
            int beat = (int) (t / 6) % 9;
            head.zRot = beat == 0 ? 0.45f : beat == 4 ? -0.3f : 0f;
            rightArm.xRot = -0.45f;
            leftArm.xRot = -0.3f;
            rightArm.zRot = 0.15f;
            leftArm.zRot = -0.1f;
        } else {
            float swing = walk * 0.6f;
            leftLeg.xRot = Mth.cos(swing) * 1.1f * speed;
            rightLeg.xRot = Mth.cos(swing + Mth.PI) * 1.1f * speed;
            rightArm.xRot = Mth.cos(swing) * 0.9f * speed - 0.25f;
            leftArm.xRot = Mth.cos(swing + Mth.PI) * 0.9f * speed - 0.25f;
            rightArm.zRot = 0.08f + Mth.sin(t * 0.07f) * 0.05f;
            leftArm.zRot = -0.08f - Mth.sin(t * 0.07f) * 0.05f;
            body.xRot = 0.18f + speed * 0.35f;
        }
        if (s.attackAnim > 0f) {
            float a = Mth.sin(s.attackAnim * Mth.PI);
            rightArm.xRot = -2.2f * a;
            leftArm.xRot = -1.8f * a;
        }
        cape.xRot = 0.1f + speed * 0.6f + Mth.sin(t * 0.09f) * 0.06f;
    }
}
