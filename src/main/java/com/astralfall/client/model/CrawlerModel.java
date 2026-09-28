package com.astralfall.client.model;

import com.astralfall.client.render.States;
import com.astralfall.entity.mob.MeteoriteCrawlerEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

public class CrawlerModel extends EntityModel<States.Crawler> {
    private final ModelPart body, head, leftMandible, rightMandible;
    private final ModelPart[] upper = new ModelPart[6];
    private final ModelPart[] lower = new ModelPart[6];

    public CrawlerModel(ModelPart root) {
        super(root);
        body = root.getChild("body");
        head = body.getChild("head");
        leftMandible = head.getChild("left_mandible");
        rightMandible = head.getChild("right_mandible");
        for (int i = 0; i < 6; i++) {
            String name = (i < 3 ? "left" : "right") + "_leg" + (i % 3);
            upper[i] = body.getChild(name);
            lower[i] = upper[i].getChild(name + "_lower");
        }
    }

    @Override
    public void setupAnim(States.Crawler s) {
        super.setupAnim(s);
        float t = s.ageInTicks;
        boolean curled = s.mode == MeteoriteCrawlerEntity.CURL || s.mode == MeteoriteCrawlerEntity.ROLL;
        if (curled) {
            body.xRot = s.roll;
            body.y -= 1.5f;
            head.xRot = 0.9f;
            for (int i = 0; i < 6; i++) {
                float side = i < 3 ? 1f : -1f;
                upper[i].zRot = side * 1.5f;
                lower[i].zRot = -side * 2.6f;
            }
            return;
        }
        float walk = s.walkAnimationPos;
        float speed = Math.min(1f, s.walkAnimationSpeed);
        head.yRot = s.yRot * Mth.DEG_TO_RAD * 0.5f;
        head.xRot = s.xRot * Mth.DEG_TO_RAD * 0.5f;
        float chew = Mth.sin(t * 0.3f) * 0.2f;
        leftMandible.yRot = -0.3f - chew;
        rightMandible.yRot = 0.3f + chew;
        for (int i = 0; i < 6; i++) {
            float side = i < 3 ? 1f : -1f;
            float phase = walk * 1.3f + (i % 3) * 2.1f + (side > 0 ? 0 : Mth.PI);
            upper[i].yRot += Mth.sin(phase) * 0.45f * speed * side;
            upper[i].zRot += Math.abs(Mth.cos(phase)) * 0.35f * speed * side;
        }
        if (s.mode == MeteoriteCrawlerEntity.STUNNED) {
            body.zRot = Mth.sin(t * 1.4f) * 0.12f;
            head.xRot = 0.4f;
        }
    }
}
