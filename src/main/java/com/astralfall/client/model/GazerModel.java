package com.astralfall.client.model;

import com.astralfall.client.render.States;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

public class GazerModel extends EntityModel<States.Gazer> {
    private final ModelPart body, topLid, bottomLid;
    private final ModelPart[][] tentacles = new ModelPart[6][3];

    public GazerModel(ModelPart root) {
        super(root);
        body = root.getChild("body");
        topLid = body.getChild("top_lid");
        bottomLid = body.getChild("bottom_lid");
        for (int i = 0; i < 6; i++) {
            tentacles[i][0] = body.getChild("tentacle" + i);
            tentacles[i][1] = tentacles[i][0].getChild("tentacle" + i + "_b");
            tentacles[i][2] = tentacles[i][1].getChild("tentacle" + i + "_c");
        }
    }

    @Override
    public void setupAnim(States.Gazer s) {
        super.setupAnim(s);
        float t = s.ageInTicks;
        body.yRot = s.yRot * Mth.DEG_TO_RAD;
        body.xRot = s.xRot * Mth.DEG_TO_RAD;
        body.y += Mth.sin(t * 0.08f) * 1.2f;
        float lid;
        if (s.charge > 0) {
            lid = 0.05f;
            body.zRot = Mth.sin(t * 2.7f) * 0.04f * s.charge;
        } else {
            float blink = t % 90f;
            lid = blink < 3 ? 1.0f : blink < 6 ? 0.5f : 0.18f;
        }
        topLid.yScale = lid;
        bottomLid.yScale = lid;
        for (int i = 0; i < 6; i++) {
            float a = i * Mth.PI / 3f;
            for (int j = 0; j < 3; j++) {
                float w = Mth.sin(t * 0.12f + i * 1.1f + j * 0.7f) * (0.2f + j * 0.08f);
                tentacles[i][j].xRot = w * Mth.cos(a) + (j == 0 ? 0.25f * Mth.sin(a) : 0f);
                tentacles[i][j].zRot = w * Mth.sin(a) - (j == 0 ? 0.25f * Mth.cos(a) : 0f);
            }
        }
    }
}
