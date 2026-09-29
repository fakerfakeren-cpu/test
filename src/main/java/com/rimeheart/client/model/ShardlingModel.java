package com.rimeheart.client.model;

import com.rimeheart.client.render.States;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

public class ShardlingModel extends EntityModel<States.Shardling> {
    private final ModelPart body, head;
    private final ModelPart[] legs = new ModelPart[6];

    public ShardlingModel(ModelPart root) {
        super(root);
        body = root.getChild("body");
        head = body.getChild("head");
        for (int i = 0; i < 6; i++) legs[i] = body.getChild("leg" + i);
    }

    @Override
    public void setupAnim(States.Shardling s) {
        super.setupAnim(s);
        float pos = s.walkAnimationPos, speed = Math.min(1f, s.walkAnimationSpeed * 1.5f);
        head.yRot = s.yRot * Mth.DEG_TO_RAD;
        head.xRot = s.xRot * Mth.DEG_TO_RAD;
        body.y += Mth.sin(s.ageInTicks * 0.2f) * 0.2f;
        for (int i = 0; i < 6; i++) {
            float phase = (i % 2 == 0 ? 0 : Mth.PI) + (i / 2) * 0.9f;
            float side = i < 3 ? 1f : -1f;
            legs[i].yRot = Mth.cos(pos * 1.6f + phase) * 0.5f * speed * side;
            legs[i].zRot = side * (0.55f + Math.abs(Mth.sin(pos * 1.6f + phase)) * 0.35f * speed);
        }
    }
}
