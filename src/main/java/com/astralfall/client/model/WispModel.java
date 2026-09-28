package com.astralfall.client.model;

import com.astralfall.client.render.States;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.util.Mth;

public class WispModel extends EntityModel<States.Wisp> {
    private final ModelPart body, leftWing, rightWing, tail1, tail2, tail3, orbit;

    public WispModel(ModelPart root) {
        super(root, RenderTypes::entityTranslucent);
        body = root.getChild("body");
        leftWing = body.getChild("left_wing");
        rightWing = body.getChild("right_wing");
        tail1 = body.getChild("tail1");
        tail2 = tail1.getChild("tail2");
        tail3 = tail2.getChild("tail3");
        orbit = body.getChild("orbit");
    }

    @Override
    public void setupAnim(States.Wisp s) {
        super.setupAnim(s);
        float t = s.ageInTicks;
        body.y += Mth.sin(t * 0.1f) * 1.5f + (s.sitting ? 4f : 0f);
        body.yRot = s.yRot * Mth.DEG_TO_RAD;
        float flap = Mth.sin(t * 0.6f) * 0.55f;
        leftWing.yRot = -0.35f - flap;
        rightWing.yRot = 0.35f + flap;
        tail1.xRot = Mth.sin(t * 0.15f) * 0.25f;
        tail2.xRot = Mth.sin(t * 0.15f - 0.6f) * 0.3f;
        tail3.xRot = Mth.sin(t * 0.15f - 1.2f) * 0.35f;
        tail1.zRot = Mth.cos(t * 0.11f) * 0.2f;
        orbit.yRot = t * 0.12f;
        orbit.xRot = Mth.sin(t * 0.05f) * 0.3f;
    }
}
