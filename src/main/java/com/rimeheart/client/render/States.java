package com.rimeheart.client.render;

import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;

/** Render states for Rimeheart entities. */
public final class States {
    private States() {}

    public static class Wraith extends LivingEntityRenderState {
        public int casting;
    }

    public static class Shardling extends LivingEntityRenderState {
    }

    public static class Sovereign extends LivingEntityRenderState {
        public int phase;
        public int attack;
        public float attackTicks;
        public int emerge;
    }
}
