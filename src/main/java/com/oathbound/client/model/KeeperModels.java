package com.oathbound.client.model;

import com.oathbound.client.render.States;
import com.oathbound.entity.boss.ArchmageVeylEntity;
import com.oathbound.entity.boss.HrodgarEntity;
import com.oathbound.entity.boss.MorvaneEntity;
import com.oathbound.entity.boss.SirCaldrisEntity;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;

/** Animated models for the three seal keepers and the Hollow King. */
public final class KeeperModels {
    private KeeperModels() {}

    abstract static class Humanoid extends Rig<States.Keeper> {
        protected final ModelPart body, head, armL, armR, legL, legR;

        Humanoid(ModelPart root, String model) {
            super(root, model);
            body = part("body");
            head = part("head");
            armL = part("left_arm");
            armR = part("right_arm");
            legL = part("left_leg");
            legR = part("right_leg");
        }

        /** Kneeling vigil while dormant. */
        protected void kneel(States.Keeper s) {
            legL.xRot = -1.4f;
            legR.xRot = 0.1f;
            hull.y = 24f + 5f;
            body.xRot = 0.35f;
            head.xRot = 0.5f;
            armL.xRot = -0.4f;
            armR.xRot = -0.4f;
        }
    }

    public static class Caldris extends Humanoid {
        private final ModelPart cape;

        public Caldris(ModelPart root) {
            super(root, "sir_caldris");
            cape = part("cape");
        }

        @Override
        public void setupAnim(States.Keeper s) {
            super.setupAnim(s);
            if (s.sleeping) {
                kneel(s);
                return;
            }
            Poses.look(head, s);
            Poses.stride(legL, legR, null, null, s, 0.8f);
            float t = s.moveTicks;
            // shield always raised before him
            armL.xRot = -1.35f;
            armL.yRot = 0.5f;
            armR.xRot = -0.3f + Mth.sin(s.walkAnimationPos * 0.66f) * 0.3f * Math.min(1, s.walkAnimationSpeed);
            switch (s.move) {
                case SirCaldrisEntity.SWING -> armR.xRot = t < 8 ? -2.6f * (t / 8f) : -2.6f + (t - 8) * 0.3f;
                case SirCaldrisEntity.CHARGE -> {
                    body.xRot = t < 16 ? 0.1f : 0.45f;
                    armL.xRot = -1.55f;
                    armL.yRot = 0.1f;
                }
                case SirCaldrisEntity.UNDERTOW -> {
                    armR.xRot = t < 34 ? -3.0f : -0.4f;
                    armR.zRot = t < 34 ? Mth.sin(t * 0.5f) * 0.3f : 0f;
                }
                case SirCaldrisEntity.STUNNED -> {
                    head.xRot = 0.6f + Mth.sin(s.ageInTicks * 0.3f) * 0.1f;
                    armL.xRot = -0.2f;
                    body.xRot = 0.3f;
                }
                default -> {}
            }
            if (s.stagger > 0) {
                armL.xRot = 0.2f;
                body.xRot = -0.2f;
                head.xRot = -0.3f;
            }
            cape.xRot = 0.1f + Math.min(1f, s.walkAnimationSpeed) * 0.5f + Mth.sin(s.ageInTicks * 0.05f) * 0.05f;
        }
    }

    public static class Veyl extends Humanoid {
        private final ModelPart halo, skirt, skirt2;

        public Veyl(ModelPart root) {
            super(root, "archmage_veyl");
            halo = part("halo");
            skirt = part("skirt");
            skirt2 = part("skirt2");
        }

        @Override
        public void setupAnim(States.Keeper s) {
            super.setupAnim(s);
            float a = s.ageInTicks;
            halo.zRot = a * 0.05f;
            if (s.sleeping) {
                // cross-legged meditation, floating
                hull.y = 24f + Mth.sin(a * 0.05f) * 1.0f;
                armL.xRot = -0.6f;
                armR.xRot = -0.6f;
                armL.zRot = 0.4f;
                armR.zRot = -0.4f;
                head.xRot = 0.3f;
                return;
            }
            Poses.look(head, s);
            hull.y = 24f + Mth.sin(a * 0.1f) * 1.5f;
            skirt.xRot = 0.1f + Mth.sin(a * 0.1f) * 0.05f;
            skirt2.xRot = 0.1f + Mth.sin(a * 0.1f + 1) * 0.08f;
            armL.xRot = -0.2f + Mth.sin(a * 0.07f) * 0.1f;
            armR.xRot = -0.5f;
            switch (s.move) {
                case ArchmageVeylEntity.ORBS -> {
                    armR.xRot = -2.2f + Mth.sin(a * 0.4f) * 0.2f;
                    armL.xRot = -1.8f;
                }
                case ArchmageVeylEntity.GLYPH, ArchmageVeylEntity.MIRROR -> {
                    armL.xRot = -2.8f;
                    armR.xRot = -2.8f;
                    armL.zRot = -0.5f;
                    armR.zRot = 0.5f;
                }
                case ArchmageVeylEntity.DAZED -> {
                    head.xRot = 0.8f;
                    armL.xRot = 0.3f;
                    armR.xRot = 0.3f;
                    halo.zRot = a * 0.4f;
                }
                default -> {}
            }
        }
    }

    public static class Hrodgar extends Humanoid {
        private final ModelPart chain, flail, cape;

        public Hrodgar(ModelPart root) {
            super(root, "hrodgar");
            chain = part("flail_chain");
            flail = part("flail_head");
            cape = part("cape");
        }

        @Override
        public void setupAnim(States.Keeper s) {
            super.setupAnim(s);
            float a = s.ageInTicks;
            if (s.sleeping) {
                // enthroned
                legL.xRot = -1.5f;
                legR.xRot = -1.5f;
                hull.y = 24f + 9f;
                armL.xRot = -0.9f;
                armR.xRot = -0.9f;
                head.xRot = 0.35f;
                chain.xRot = 0.9f;
                return;
            }
            Poses.look(head, s);
            Poses.stride(legL, legR, armL, null, s, 0.7f);
            float t = s.moveTicks;
            armR.xRot = -0.4f;
            chain.xRot = Mth.sin(a * 0.15f) * 0.3f;
            chain.zRot = Mth.cos(a * 0.15f) * 0.2f;
            switch (s.move) {
                case HrodgarEntity.SWEEP -> {
                    armR.xRot = -1.4f;
                    armR.yRot = t < 14 ? 0.9f * (t / 14f) : 0.9f - (t - 14) * 0.25f;
                    chain.xRot = -1.2f;
                }
                case HrodgarEntity.SLAM -> {
                    armL.xRot = t < 12 ? -2.9f : -0.5f;
                    armR.xRot = t < 12 ? -2.9f : -0.5f;
                    chain.xRot = t < 12 ? -2.5f : 0.5f;
                }
                case HrodgarEntity.RAISE, HrodgarEntity.DEVOUR -> {
                    armL.xRot = -2.6f;
                    armR.xRot = -2.6f;
                    armL.zRot = -0.6f;
                    armR.zRot = 0.6f;
                    head.xRot = -0.5f;
                }
                default -> {}
            }
            cape.xRot = 0.1f + Math.min(1f, s.walkAnimationSpeed) * 0.4f;
            flail.yRot = a * 0.1f;
        }
    }

    public static class Morvane extends Humanoid {
        private final ModelPart sword, cape, crown;

        public Morvane(ModelPart root) {
            super(root, "morvane");
            sword = part("sword");
            cape = part("cape");
            crown = part("crown");
        }

        @Override
        public void setupAnim(States.Keeper s) {
            super.setupAnim(s);
            float a = s.ageInTicks;
            if (s.sleeping) {
                // seated on the throne, sword across his knees
                legL.xRot = -1.5f;
                legR.xRot = -1.5f;
                hull.y = 24f + 8f;
                armR.xRot = -1.0f;
                armL.xRot = -1.0f;
                armR.zRot = 0.3f;
                head.xRot = 0.4f;
                return;
            }
            Poses.look(head, s);
            Poses.stride(legL, legR, armL, null, s, 0.8f);
            float t = s.moveTicks;
            armR.xRot = -0.5f;
            crown.yRot = s.phase >= 2 ? a * 0.03f : 0f;
            switch (s.move) {
                case MorvaneEntity.COMBO -> {
                    float cut = (t % 14) / 14f;
                    armR.xRot = -2.6f + cut * 2.8f;
                    armR.yRot = (t / 14 % 2 == 0 ? 0.6f : -0.6f) * (1 - cut * 2);
                }
                case MorvaneEntity.LUNGE -> {
                    // draw the blade back and up, then drive it straight out
                    armR.xRot = t < 14 ? -1.1f : -0.15f;
                    body.xRot = t < 14 ? -0.1f : 0.5f;
                    legL.xRot = t < 14 ? 0.3f : -0.8f;
                    legR.xRot = t < 14 ? -0.3f : 0.9f;
                }
                case MorvaneEntity.RUIN -> {
                    armR.xRot = -1.3f;
                    armR.yRot = -0.9f;
                    armL.xRot = -1.3f;
                    armL.yRot = 0.6f;
                }
                case MorvaneEntity.BLADES, MorvaneEntity.PILLARS, MorvaneEntity.FORSWORN, MorvaneEntity.TRANSITION, MorvaneEntity.RISING -> {
                    armL.xRot = -2.9f;
                    armR.xRot = -2.9f;
                    armL.zRot = -0.4f;
                    armR.zRot = 0.4f;
                    head.xRot = -0.4f;
                }
                case MorvaneEntity.UNVEILED -> {
                    kneel(s);
                    head.xRot = 0.8f + Mth.sin(a * 0.2f) * 0.05f;
                }
                default -> {}
            }
            if (s.phase >= 2 && s.move != MorvaneEntity.UNVEILED) {
                legL.xRot = 0.3f + Mth.sin(a * 0.1f) * 0.1f;
                legR.xRot = 0.2f + Mth.cos(a * 0.1f) * 0.1f;
            }
            cape.xRot = 0.15f + Mth.sin(a * 0.06f) * 0.08f + Math.min(1f, s.walkAnimationSpeed) * 0.4f;
            sword.xRot = 0f;
        }
    }
}
