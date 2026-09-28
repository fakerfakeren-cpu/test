package com.astralfall.client.render;

import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;

/** Render states for Astralfall entities. */
public final class States {
    private States() {}

    public static class Wisp extends LivingEntityRenderState {
        public boolean prismatic;
        public boolean sitting;
    }

    public static class Stalker extends LivingEntityRenderState {
        public boolean frozen;
        public float attackAnim;
    }

    public static class Crawler extends LivingEntityRenderState {
        public int mode;
        public float roll;
    }

    public static class Gazer extends LivingEntityRenderState {
        public float charge;
    }

    public static class Titan extends LivingEntityRenderState {
        public int phase;
        public int attack;
        public float attackTicks;
        public float emerge;
        public int shards;
    }

    public static class Meteor extends EntityRenderState {
        public float spin;
        public float size;
        public int variant;
    }

    public static class Singularity extends EntityRenderState {
        public float progress;
        public float radius;
    }
}
