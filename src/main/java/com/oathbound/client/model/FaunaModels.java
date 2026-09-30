package com.oathbound.client.model;

import com.oathbound.client.render.States;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/**
 * Animation rigs for the wider roster, one per body plan. Parts a model does not have are simply skipped, so a
 * deer, a hare and a boar share the quadruped rig with their own gait settings.
 */
public final class FaunaModels {
    private FaunaModels() {}

    private static void sway(ModelPart p, float age, float speed, float amount, float base) {
        if (p != null) p.yRot = base + Mth.sin(age * speed) * amount;
    }

    // ------------------------------------------------------------------ four legs
    public static class Quadruped extends Rig<States.Fauna> {
        private final ModelPart body, head, jaw, tail, earL, earR, legFL, legFR, legBL, legBR, saddle;
        private final float stride, headDown;
        private final boolean hop;

        /**
         * @param stride   how far the legs swing
         * @param hop      a hare's gait: the pairs move together and the body bounds
         * @param headDown how far the head drops for the special action (grazing, charging)
         */
        public Quadruped(ModelPart root, String model, float stride, boolean hop, float headDown) {
            super(root, model);
            body = opt("body");
            head = opt("head");
            jaw = opt("jaw");
            tail = opt("tail");
            earL = opt("ear_l");
            earR = opt("ear_r");
            saddle = opt("saddle");
            legFL = opt("leg_fl");
            legFR = opt("leg_fr");
            legBL = opt("leg_bl");
            legBR = opt("leg_br");
            this.stride = stride;
            this.hop = hop;
            this.headDown = headDown;
        }

        @Override
        public void setupAnim(States.Fauna s) {
            super.setupAnim(s);
            if (saddle != null) saddle.visible = s.variant == 1;
            float p = s.walkAnimationPos * 0.6662f, sp = Math.min(1f, s.walkAnimationSpeed) * stride;
            if (head != null) {
                head.yRot = s.yRot * Mth.DEG_TO_RAD * 0.8f;
                head.xRot = s.xRot * Mth.DEG_TO_RAD * 0.6f + (s.action ? headDown : 0f);
            }
            if (hop) {
                float h = Mth.cos(p) * sp;
                if (legFL != null) legFL.xRot = h * 1.2f;
                if (legFR != null) legFR.xRot = h * 1.2f;
                if (legBL != null) legBL.xRot = -h * 1.4f;
                if (legBR != null) legBR.xRot = -h * 1.4f;
                if (body != null) body.y += -Math.abs(Mth.sin(p)) * 2.0f * sp;
            } else {
                if (legFL != null) legFL.xRot = Mth.cos(p) * 1.3f * sp;
                if (legBR != null) legBR.xRot = Mth.cos(p) * 1.3f * sp;
                if (legFR != null) legFR.xRot = Mth.cos(p + Mth.PI) * 1.3f * sp;
                if (legBL != null) legBL.xRot = Mth.cos(p + Mth.PI) * 1.3f * sp;
            }
            if (tail != null) {
                tail.xRot = 0.4f + Mth.sin(s.ageInTicks * 0.15f) * 0.08f;
                tail.yRot = Mth.sin(s.ageInTicks * 0.25f) * 0.25f;
            }
            if (earL != null) earL.zRot = 0.2f + Mth.sin(s.ageInTicks * 0.1f) * 0.08f;
            if (earR != null) earR.zRot = -0.2f - Mth.sin(s.ageInTicks * 0.1f + 1f) * 0.08f;
            if (jaw != null) jaw.xRot = 0.05f + Poses.arc(s.attack) * 0.7f;
            if (s.attack > 0 && head != null) head.xRot += -Poses.arc(s.attack) * 0.4f;
        }
    }

    // ------------------------------------------------------------------ two legs
    public static class Biped extends Rig<States.Fauna> {
        private final ModelPart head, body, armL, armR, legL, legR, robe;
        private final float stride, hunch;

        public Biped(ModelPart root, String model, float stride, float hunch) {
            super(root, model);
            head = opt("head");
            body = opt("body");
            armL = opt("left_arm");
            armR = opt("right_arm");
            legL = opt("left_leg");
            legR = opt("right_leg");
            robe = opt("robe");
            this.stride = stride;
            this.hunch = hunch;
        }

        @Override
        public void setupAnim(States.Fauna s) {
            super.setupAnim(s);
            if (head != null) Poses.look(head, s);
            Poses.stride(legL, legR, armL, armR, s, stride);
            if (body != null) body.xRot = hunch;
            if (robe != null) robe.xRot = Math.abs(Mth.sin(s.walkAnimationPos * 0.6662f)) * 0.15f * Math.min(1f, s.walkAnimationSpeed);
            if (armL != null) armL.zRot = -0.08f - Mth.sin(s.ageInTicks * 0.07f) * 0.04f;
            if (armR != null) armR.zRot = 0.08f + Mth.sin(s.ageInTicks * 0.07f) * 0.04f;
            if (s.action) {
                // casting or singing: both arms raised
                if (armL != null) armL.xRot = -2.4f + Mth.sin(s.ageInTicks * 0.3f) * 0.1f;
                if (armR != null) armR.xRot = -2.4f - Mth.sin(s.ageInTicks * 0.3f) * 0.1f;
            } else if (s.attack > 0 && armR != null) {
                armR.xRot = -1.9f + Poses.arc(s.attack) * -0.6f + s.attack * 2.3f;
            }
        }
    }

    // ------------------------------------------------------------------ many legs
    public static class Crawler extends Rig<States.Fauna> {
        private final ModelPart body, head;
        private final ModelPart[] legs = new ModelPart[8];

        public Crawler(ModelPart root, String model) {
            super(root, model);
            body = opt("body");
            head = opt("head");
            for (int i = 0; i < legs.length; i++) legs[i] = opt("leg_" + i);
        }

        @Override
        public void setupAnim(States.Fauna s) {
            super.setupAnim(s);
            float p = s.walkAnimationPos * 1.2f, sp = Math.min(1f, s.walkAnimationSpeed);
            for (int i = 0; i < legs.length; i++) {
                if (legs[i] == null) continue;
                float side = i % 2 == 0 ? 1 : -1;
                float phase = p + i * Mth.PI / 2;
                legs[i].yRot = side * Mth.cos(phase) * 0.45f * sp;
                legs[i].zRot = side * (0.35f + Math.max(0, Mth.sin(phase)) * 0.4f * sp);
            }
            if (head != null) {
                head.yRot = s.yRot * Mth.DEG_TO_RAD * 0.5f;
                head.xRot = -Poses.arc(s.attack) * 0.5f;
            }
            if (body != null) body.y += Mth.sin(s.ageInTicks * 0.2f) * 0.2f;
        }
    }

    // ------------------------------------------------------------------ things that float
    public static class Floater extends Rig<States.Fauna> {
        private final ModelPart body, head, cloak, armL, armR;
        private final ModelPart[] orbits = new ModelPart[3];

        public Floater(ModelPart root, String model) {
            super(root, model);
            body = opt("body");
            head = opt("head");
            cloak = opt("cloak");
            armL = opt("left_arm");
            armR = opt("right_arm");
            for (int i = 0; i < orbits.length; i++) orbits[i] = opt("orbit_" + i);
        }

        @Override
        public void setupAnim(States.Fauna s) {
            super.setupAnim(s);
            hull.y += Mth.sin(s.ageInTicks * 0.1f) * 1.2f;
            if (head != null) Poses.look(head, s);
            for (int i = 0; i < orbits.length; i++) {
                if (orbits[i] == null) continue;
                orbits[i].yRot = s.ageInTicks * (0.05f + i * 0.03f) * (i % 2 == 0 ? 1 : -1);
                orbits[i].xRot = 0.3f * (i + 1) + Mth.sin(s.ageInTicks * 0.02f + i) * 0.2f;
            }
            if (cloak != null) cloak.xRot = 0.12f + Mth.sin(s.ageInTicks * 0.12f) * 0.08f + Math.min(1f, s.walkAnimationSpeed) * 0.5f;
            if (armL != null) armL.xRot = -0.3f + Mth.sin(s.ageInTicks * 0.09f) * 0.15f - (s.action ? 1.8f : 0f);
            if (armR != null) armR.xRot = -0.3f - Mth.sin(s.ageInTicks * 0.09f) * 0.15f - (s.action ? 1.8f : 0f) - Poses.arc(s.attack) * 1.2f;
            if (body != null && s.action) body.xRot = 0.35f;
        }
    }

    // ------------------------------------------------------------------ birds
    public static class Bird extends Rig<States.Fauna> {
        private final ModelPart body, neck, head, wingL, wingR, legL, legR, tail;

        public Bird(ModelPart root, String model) {
            super(root, model);
            body = opt("body");
            neck = opt("neck");
            head = opt("head");
            wingL = opt("left_wing");
            wingR = opt("right_wing");
            legL = opt("left_leg");
            legR = opt("right_leg");
            tail = opt("tail");
        }

        @Override
        public void setupAnim(States.Fauna s) {
            super.setupAnim(s);
            float p = s.walkAnimationPos * 0.9f, sp = Math.min(1f, s.walkAnimationSpeed);
            if (legL != null) legL.xRot = Mth.cos(p) * 0.9f * sp;
            if (legR != null) legR.xRot = Mth.cos(p + Mth.PI) * 0.9f * sp;
            if (head != null) head.yRot = s.yRot * Mth.DEG_TO_RAD;
            // fishing: the neck strikes down
            if (neck != null) neck.xRot = s.action ? 1.3f : Mth.sin(s.ageInTicks * 0.05f) * 0.08f;
            float flap = s.action ? 0f : (sp > 0.6f ? Mth.sin(s.ageInTicks * 0.9f) * 0.9f : 0f);
            if (wingL != null) wingL.zRot = -0.1f - flap;
            if (wingR != null) wingR.zRot = 0.1f + flap;
            if (tail != null) tail.xRot = 0.2f + Mth.sin(s.ageInTicks * 0.1f) * 0.05f;
        }
    }
}
