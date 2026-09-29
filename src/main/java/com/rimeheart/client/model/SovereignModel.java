package com.rimeheart.client.model;

import com.rimeheart.client.render.States;
import com.rimeheart.entity.boss.FrostSovereignEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

public class SovereignModel extends EntityModel<States.Sovereign> {
    private final ModelPart body, head, leftArm, rightArm, leftForearm, rightForearm, skirt, skirt2, skirt3, orbit;

    public SovereignModel(ModelPart root) {
        super(root);
        body = root.getChild("body");
        head = body.getChild("head");
        leftArm = body.getChild("left_arm");
        rightArm = body.getChild("right_arm");
        leftForearm = leftArm.getChild("left_forearm");
        rightForearm = rightArm.getChild("right_forearm");
        skirt = body.getChild("skirt");
        skirt2 = skirt.getChild("skirt2");
        skirt3 = skirt2.getChild("skirt3");
        orbit = root.getChild("orbit");
    }

    private static float ramp(float t, float over) {
        return Mth.clamp(t / over, 0f, 1f);
    }

    @Override
    public void setupAnim(States.Sovereign s) {
        super.setupAnim(s);
        float t = s.ageInTicks;
        body.y += Mth.sin(t * 0.06f) * 1.2f;
        head.yRot = s.yRot * Mth.DEG_TO_RAD * 0.6f;
        head.xRot = s.xRot * Mth.DEG_TO_RAD * 0.5f;
        skirt.xRot = 0.08f + Mth.sin(t * 0.05f) * 0.08f;
        skirt2.xRot = Mth.sin(t * 0.05f - 0.6f) * 0.12f;
        skirt3.xRot = Mth.sin(t * 0.05f - 1.2f) * 0.16f;
        skirt2.zRot = Mth.cos(t * 0.04f) * 0.08f;
        orbit.yRot = t * (s.phase >= 2 ? 0.06f : 0.03f);
        leftArm.xRot = Mth.sin(t * 0.05f) * 0.08f;
        rightArm.xRot = -Mth.sin(t * 0.05f) * 0.08f;
        leftArm.zRot = -0.12f;
        rightArm.zRot = 0.12f;
        leftForearm.xRot = -0.3f;
        rightForearm.xRot = -0.3f;
        if (s.emerge > 0) {
            head.xRot = 0.5f;
            leftArm.xRot = -2.6f;
            rightArm.xRot = -2.6f;
            leftForearm.xRot = -0.2f;
            rightForearm.xRot = -0.2f;
            return;
        }
        if (s.deathTime > 0) {
            body.zRot = Mth.sin(t * 2.1f) * 0.06f;
            head.xRot = -0.7f;
            leftArm.zRot = -1.1f;
            rightArm.zRot = 1.1f;
            return;
        }
        float a = s.attackTicks;
        switch (s.attack) {
            case FrostSovereignEntity.BARRAGE -> {
                float up = ramp(a, 8);
                leftArm.xRot = -2.8f * up;
                rightArm.xRot = -2.8f * up;
                leftArm.zRot = -0.4f * up;
                rightArm.zRot = 0.4f * up;
            }
            case FrostSovereignEntity.ERUPTION -> {
                float raise = a < 26 ? ramp(a, 12) : 1f - ramp(a - 26, 4);
                rightArm.xRot = -2.9f * raise;
                rightForearm.xRot = -0.2f;
                if (a >= 26) rightArm.xRot = -0.2f;
            }
            case FrostSovereignEntity.BREATH -> {
                head.xRot = 0.35f;
                leftArm.xRot = -0.6f;
                rightArm.xRot = -0.6f;
                leftArm.zRot = -0.7f;
                rightArm.zRot = 0.7f;
            }
            case FrostSovereignEntity.STOMP -> {
                float lift = a < 15 ? ramp(a, 12) : 1f - ramp(a - 15, 3);
                leftArm.xRot = -3.0f * lift;
                rightArm.xRot = -3.0f * lift;
                leftForearm.xRot = -0.9f * lift;
                rightForearm.xRot = -0.9f * lift;
            }
            case FrostSovereignEntity.SUMMON, FrostSovereignEntity.TRANSITION -> {
                leftArm.zRot = -1.3f;
                rightArm.zRot = 1.3f;
                head.xRot = -0.5f;
            }
            default -> {
            }
        }
    }
}
