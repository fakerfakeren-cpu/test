package com.astralfall.client.model;

import com.astralfall.client.render.States;
import com.astralfall.entity.boss.AstraeusEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

public class AstraeusModel extends EntityModel<States.Titan> {
    private final ModelPart torso, head, halo, leftArm, rightArm, leftForearm, rightForearm, tail, tail2, tail3, tail4, orbit;
    private final ModelPart[] shards = new ModelPart[6];

    public AstraeusModel(ModelPart root) {
        super(root);
        torso = root.getChild("torso");
        head = torso.getChild("head");
        halo = head.getChild("halo");
        leftArm = torso.getChild("left_arm");
        rightArm = torso.getChild("right_arm");
        leftForearm = leftArm.getChild("left_forearm");
        rightForearm = rightArm.getChild("right_forearm");
        tail = torso.getChild("tail");
        tail2 = tail.getChild("tail2");
        tail3 = tail2.getChild("tail3");
        tail4 = tail3.getChild("tail4");
        orbit = root.getChild("orbit");
        for (int i = 0; i < 6; i++) shards[i] = orbit.getChild("shard" + i);
    }

    private static float ramp(float t, float over) {
        return Mth.clamp(t / over, 0f, 1f);
    }

    @Override
    public void setupAnim(States.Titan s) {
        super.setupAnim(s);
        float t = s.ageInTicks;
        boolean enraged = s.phase >= 2;
        torso.y += Mth.sin(t * 0.06f) * 1.5f;
        torso.yScale = 1.0f + Mth.sin(t * 0.09f) * 0.015f;
        head.yRot = s.yRot * Mth.DEG_TO_RAD * 0.6f;
        head.xRot = s.xRot * Mth.DEG_TO_RAD * 0.5f;
        halo.zRot = t * (enraged ? 0.09f : 0.03f);
        tail.xRot = 0.12f + Mth.sin(t * 0.05f) * 0.12f;
        tail2.xRot = Mth.sin(t * 0.05f - 0.5f) * 0.18f;
        tail3.xRot = Mth.sin(t * 0.05f - 1.0f) * 0.22f;
        tail4.xRot = Mth.sin(t * 0.05f - 1.5f) * 0.26f;
        tail.zRot = Mth.cos(t * 0.04f) * 0.08f;
        tail3.zRot = Mth.cos(t * 0.04f - 1f) * 0.15f;
        orbit.yRot = t * (enraged ? 0.07f : 0.04f);
        for (int i = 0; i < 6; i++) {
            shards[i].visible = i < s.shards;
            shards[i].yRot = t * 0.15f + i;
            shards[i].y = Mth.sin(t * 0.1f + i) * 2f;
        }
        leftArm.xRot = Mth.sin(t * 0.05f) * 0.08f;
        rightArm.xRot = -Mth.sin(t * 0.05f) * 0.08f;
        leftForearm.xRot = -0.35f;
        rightForearm.xRot = -0.35f;

        if (s.emerge > 0) {
            head.xRot = 0.6f;
            leftArm.xRot = -1.0f;
            rightArm.xRot = -1.0f;
            leftArm.zRot = 0.6f;
            rightArm.zRot = -0.6f;
            leftForearm.xRot = -1.2f;
            rightForearm.xRot = -1.2f;
            return;
        }
        if (s.deathTime > 0) {
            torso.zRot = Mth.sin(t * 2.3f) * 0.08f;
            head.xRot = -0.8f;
            leftArm.zRot = -1.2f;
            rightArm.zRot = 1.2f;
            return;
        }
        float a = s.attackTicks;
        switch (s.attack) {
            case AstraeusEntity.METEOR_RAIN -> {
                float up = ramp(a, 12);
                leftArm.xRot = -2.9f * up;
                rightArm.xRot = -2.9f * up;
                leftForearm.xRot = 0f;
                rightForearm.xRot = 0f;
                head.xRot = -0.5f * up;
            }
            case AstraeusEntity.STAR_LANCE -> {
                float charge = ramp(a, 30);
                if (a < 30) {
                    leftArm.zRot = -1.0f * charge;
                    rightArm.zRot = 1.0f * charge;
                    leftArm.xRot = -0.6f * charge;
                    rightArm.xRot = -0.6f * charge;
                } else {
                    leftArm.xRot = -1.45f;
                    rightArm.xRot = -1.45f;
                    leftArm.zRot = -0.25f;
                    rightArm.zRot = 0.25f;
                    leftForearm.xRot = 0f;
                    rightForearm.xRot = 0f;
                }
            }
            case AstraeusEntity.SHARD_BARRAGE -> {
                rightArm.xRot = -1.3f - Mth.sin(a * 0.5f) * 0.6f;
                rightArm.zRot = 0.3f;
            }
            case AstraeusEntity.GRAVITY_COLLAPSE -> {
                if (a < 50) {
                    float o = ramp(a, 15);
                    leftArm.zRot = -1.35f * o;
                    rightArm.zRot = 1.35f * o;
                    leftForearm.xRot = -1.0f * o;
                    rightForearm.xRot = -1.0f * o;
                    torso.zRot = Mth.sin(t * 1.9f) * 0.03f;
                } else {
                    leftArm.xRot = 0.4f;
                    rightArm.xRot = 0.4f;
                }
            }
            case AstraeusEntity.SUMMON -> {
                float o = ramp(a, 20);
                leftArm.zRot = -2.2f * o;
                rightArm.zRot = 2.2f * o;
                head.xRot = -0.5f * o;
            }
            case AstraeusEntity.SINGULARITY -> {
                rightArm.xRot = -1.6f;
                rightForearm.xRot = 0f;
            }
            case AstraeusEntity.SLAM -> {
                if (a < 18) {
                    float o = ramp(a, 14);
                    leftArm.xRot = -2.7f * o;
                    rightArm.xRot = -2.7f * o;
                    leftForearm.xRot = 0f;
                    rightForearm.xRot = 0f;
                } else {
                    float o = ramp(a - 18, 4);
                    leftArm.xRot = -2.7f + 3.0f * o;
                    rightArm.xRot = -2.7f + 3.0f * o;
                }
            }
            case AstraeusEntity.TRANSITION -> {
                head.xRot = -0.75f;
                leftArm.zRot = -1.1f;
                rightArm.zRot = 1.1f;
                torso.zRot = Mth.sin(t * 2.1f) * 0.05f;
                torso.xRot = -0.15f;
            }
            default -> {}
        }
    }
}
