package com.oathbound.client.model;

import com.oathbound.client.render.States;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** Animated models for Oathbound's everyday creatures. */
public final class CreatureModels {
    private CreatureModels() {}

    public static class Moth extends Rig<States.Moth> {
        private final ModelPart wingL, wingR, body;

        public Moth(ModelPart root) {
            super(root, "lanternmoth");
            body = part("body");
            wingL = part("left_wing");
            wingR = part("right_wing");
        }

        @Override
        public void setupAnim(States.Moth s) {
            super.setupAnim(s);
            float flap = Mth.sin(s.ageInTicks * 1.3f) * 0.9f;
            wingL.zRot = -0.2f - flap;
            wingR.zRot = 0.2f + flap;
            body.xRot = -0.25f + Mth.sin(s.ageInTicks * 0.2f) * 0.1f;
            hull.y = 24f + Mth.sin(s.ageInTicks * 0.3f) * 0.8f;
        }
    }

    public static class Gloamling extends Rig<States.Gloamling> {
        private final ModelPart head, armL, armR, legL, legR, tail, body;

        public Gloamling(ModelPart root) {
            super(root, "gloamling");
            body = part("body");
            head = part("head");
            armL = part("left_arm");
            armR = part("right_arm");
            legL = part("left_leg");
            legR = part("right_leg");
            tail = part("tail");
        }

        @Override
        public void setupAnim(States.Gloamling s) {
            super.setupAnim(s);
            Poses.look(head, s);
            Poses.stride(legL, legR, armL, armR, s, 1.1f);
            body.xRot = 0.35f + Math.min(1f, s.walkAnimationSpeed) * 0.3f;
            armL.zRot = -0.25f - Mth.sin(s.ageInTicks * 0.2f) * 0.1f;
            armR.zRot = 0.25f + Mth.sin(s.ageInTicks * 0.2f) * 0.1f;
            tail.yRot = Mth.sin(s.ageInTicks * 0.25f) * 0.5f;
            tail.xRot = 0.5f;
            if (s.attack > 0) {
                float a = Poses.arc(s.attack);
                armL.xRot = -2.0f * a;
                armR.xRot = -2.0f * a;
            }
        }
    }

    public static class Knight extends Rig<States.Knight> {
        private final ModelPart head, armL, armR, legL, legR, cape;

        public Knight(ModelPart root) {
            super(root, "forsworn_knight");
            head = part("head");
            armL = part("left_arm");
            armR = part("right_arm");
            legL = part("left_leg");
            legR = part("right_leg");
            cape = part("cape");
        }

        @Override
        public void setupAnim(States.Knight s) {
            super.setupAnim(s);
            if (s.fallen) {
                // collapsed into a heap of armour; it stirs just before it rises
                float stir = s.fallenTicks > 90 ? Mth.sin(s.ageInTicks * 1.4f) * 0.08f : 0f;
                hull.xRot = -1.45f + stir;
                hull.y = 22.5f;
                armL.zRot = -1.0f;
                armR.zRot = 1.2f;
                head.xRot = 0.6f;
                return;
            }
            Poses.look(head, s);
            Poses.stride(legL, legR, armL, armR, s, 0.9f);
            armR.xRot = armR.xRot * 0.5f - 0.35f;
            if (s.attack > 0) armR.xRot = -1.9f + Poses.arc(s.attack) * -0.6f + s.attack * 2.3f;
            cape.xRot = 0.08f + Math.min(1f, s.walkAnimationSpeed) * 0.5f + Mth.sin(s.ageInTicks * 0.08f) * 0.04f;
        }
    }

    public static class Wight extends Rig<States.Wight> {
        private final ModelPart head, armL, armR, tail1, tail2;

        public Wight(ModelPart root) {
            super(root, "barrow_wight");
            head = part("head");
            armL = part("left_arm");
            armR = part("right_arm");
            tail1 = part("tail1");
            tail2 = part("tail2");
        }

        @Override
        public void setupAnim(States.Wight s) {
            super.setupAnim(s);
            Poses.look(head, s);
            float t = s.ageInTicks;
            armL.xRot = -1.2f + Mth.sin(t * 0.1f) * 0.2f;
            armR.xRot = -1.2f + Mth.cos(t * 0.1f) * 0.2f;
            armL.zRot = -0.2f;
            armR.zRot = 0.2f;
            tail1.xRot = 0.3f + Mth.sin(t * 0.15f) * 0.15f;
            tail2.xRot = 0.3f + Mth.sin(t * 0.15f + 1) * 0.25f;
            hull.y = 24f + Mth.sin(t * 0.08f) * 1.2f;
        }
    }

    public static class Tome extends Rig<States.Tome> {
        private final ModelPart coverL, coverR, pages;

        public Tome(ModelPart root) {
            super(root, "animated_tome");
            coverL = part("cover_left");
            coverR = part("cover_right");
            pages = part("pages");
        }

        @Override
        public void setupAnim(States.Tome s) {
            super.setupAnim(s);
            float t = s.ageInTicks;
            float open = s.casting > 0 ? 1.35f : 0.7f + Mth.sin(t * 0.5f) * 0.45f;
            coverL.zRot = -open;
            coverR.zRot = open;
            pages.yRot = Mth.sin(t * 0.9f) * 0.2f;
            hull.y = 20f + Mth.sin(t * 0.25f) * 1.0f;
            hull.xRot = s.casting > 0 ? -0.6f : 0f;
        }
    }

    public static class Hound extends Rig<States.Hound> {
        private final ModelPart head, jaw, legFL, legFR, legBL, legBR, tail, body;

        public Hound(ModelPart root) {
            super(root, "veilhound");
            body = part("body");
            head = part("head");
            jaw = part("jaw");
            legFL = part("leg_fl");
            legFR = part("leg_fr");
            legBL = part("leg_bl");
            legBR = part("leg_br");
            tail = part("tail");
        }

        @Override
        public void setupAnim(States.Hound s) {
            super.setupAnim(s);
            head.yRot = s.yRot * Mth.DEG_TO_RAD * 0.7f;
            head.xRot = s.xRot * Mth.DEG_TO_RAD * 0.5f;
            float p = s.walkAnimationPos * 0.6662f, sp = Math.min(1f, s.walkAnimationSpeed);
            legFL.xRot = Mth.cos(p) * 1.3f * sp;
            legBR.xRot = Mth.cos(p) * 1.3f * sp;
            legFR.xRot = Mth.cos(p + Mth.PI) * 1.3f * sp;
            legBL.xRot = Mth.cos(p + Mth.PI) * 1.3f * sp;
            tail.xRot = 0.6f + Mth.sin(s.ageInTicks * 0.2f) * 0.1f;
            tail.yRot = Mth.sin(s.ageInTicks * 0.3f) * 0.3f;
            jaw.xRot = 0.1f + Mth.sin(s.ageInTicks * 0.15f) * 0.05f;
            if (s.lunging) {
                jaw.xRot = 0.8f;
                legFL.xRot = legFR.xRot = -1.2f;
                legBL.xRot = legBR.xRot = 1.1f;
                body.xRot = -0.2f;
            }
        }
    }

    public static class Housecarl extends Rig<States.Housecarl> {
        private final ModelPart head, armL, armR, legL, legR;

        public Housecarl(ModelPart root) {
            super(root, "spectral_housecarl");
            head = part("head");
            armL = part("left_arm");
            armR = part("right_arm");
            legL = part("left_leg");
            legR = part("right_leg");
        }

        @Override
        public void setupAnim(States.Housecarl s) {
            super.setupAnim(s);
            Poses.look(head, s);
            Poses.stride(legL, legR, armL, armR, s, 1.0f);
            armL.xRot = -0.9f;
            armL.yRot = 0.4f;
            if (s.attack > 0) armR.xRot = -2.4f + s.attack * 3.0f;
        }
    }

    /** The Crown of Blades: a single spectral sword. */
    public static class Blade extends Rig<States.Blade> {
        public Blade(ModelPart root) {
            super(root, "crown_blade");
        }

        @Override
        public void setupAnim(States.Blade s) {
            super.setupAnim(s);
            hull.yRot = s.yaw * Mth.DEG_TO_RAD;
            // the blade points along +y at rest: tip it over onto its flight line, or hang it point-down
            hull.xRot = s.launched ? (90f - s.pitch) * Mth.DEG_TO_RAD : Mth.PI;
            if (!s.launched) hull.yRot = s.ageInTicks * 0.15f;
        }
    }
}
