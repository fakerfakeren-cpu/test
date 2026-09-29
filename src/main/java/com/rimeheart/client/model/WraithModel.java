package com.rimeheart.client.model;

import com.rimeheart.client.render.States;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.util.Mth;

public class WraithModel extends EntityModel<States.Wraith> {
    private final ModelPart body, head, leftArm, rightArm, tail, tail2;

    public WraithModel(ModelPart root) {
        super(root, RenderTypes::entityTranslucent);
        body = root.getChild("body");
        head = body.getChild("head");
        leftArm = body.getChild("left_arm");
        rightArm = body.getChild("right_arm");
        tail = body.getChild("tail");
        tail2 = tail.getChild("tail2");
    }

    @Override
    public void setupAnim(States.Wraith s) {
        super.setupAnim(s);
        float t = s.ageInTicks;
        body.y += Mth.sin(t * 0.1f) * 1.2f;
        body.xRot = 0.12f + s.walkAnimationSpeed * 0.3f;
        head.yRot = s.yRot * Mth.DEG_TO_RAD;
        head.xRot = s.xRot * Mth.DEG_TO_RAD * 0.7f;
        tail.xRot = 0.2f + Mth.sin(t * 0.12f) * 0.15f;
        tail2.xRot = 0.25f + Mth.sin(t * 0.12f - 0.8f) * 0.25f;
        tail.zRot = Mth.cos(t * 0.09f) * 0.1f;
        if (s.casting > 0) {
            float c = Mth.clamp(s.casting / 12f, 0f, 1f);
            leftArm.xRot = -1.6f * c - 0.2f;
            rightArm.xRot = -1.6f * c - 0.2f;
            leftArm.zRot = -0.25f + Mth.sin(t * 0.8f) * 0.05f;
            rightArm.zRot = 0.25f - Mth.sin(t * 0.8f) * 0.05f;
        } else {
            leftArm.xRot = -0.35f + Mth.sin(t * 0.08f) * 0.12f;
            rightArm.xRot = -0.35f - Mth.sin(t * 0.08f) * 0.12f;
        }
    }
}
