package com.oathbound.client.render;

import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;

/** Render states: the per-frame snapshot each renderer extracts from its entity. */
public final class States {
    private States() {}

    public static class Moth extends LivingEntityRenderState {}

    public static class Gloamling extends LivingEntityRenderState {
        public boolean veiled;
        public float attack;
    }

    public static class Knight extends LivingEntityRenderState {
        public boolean fallen;
        public float fallenTicks;
        public float attack;
    }

    public static class Wight extends LivingEntityRenderState {}

    public static class Tome extends LivingEntityRenderState {
        public int casting;
    }

    public static class Hound extends LivingEntityRenderState {
        public boolean lunging;
    }

    public static class Housecarl extends LivingEntityRenderState {
        public boolean ally;
        public float attack;
    }

    /** Shared by the seal keepers and the Hollow King. */
    public static class Keeper extends LivingEntityRenderState {
        public boolean sleeping;
        public int move;
        public float moveTicks;
        public int stagger;
        public boolean illusion;
        public int tethers;
        public int phase;
        public boolean hollow;
    }

    public static class Blade extends EntityRenderState {
        public boolean launched;
        public float yaw;
        public float pitch;
    }
}
