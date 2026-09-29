package com.oathbound.client.model;

import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.util.Mth;

/** Small animation vocabulary shared by the Oathbound models. */
final class Poses {
    private Poses() {}

    static void look(ModelPart head, LivingEntityRenderState s) {
        head.yRot = s.yRot * Mth.DEG_TO_RAD;
        head.xRot = s.xRot * Mth.DEG_TO_RAD;
    }

    /** Opposed limb swing for a biped. */
    static void stride(ModelPart legL, ModelPart legR, ModelPart armL, ModelPart armR, LivingEntityRenderState s, float amount) {
        float p = s.walkAnimationPos * 0.6662f;
        float sp = Math.min(1f, s.walkAnimationSpeed) * amount;
        if (legL != null) legL.xRot = Mth.cos(p) * 1.2f * sp;
        if (legR != null) legR.xRot = Mth.cos(p + Mth.PI) * 1.2f * sp;
        if (armL != null) armL.xRot = Mth.cos(p + Mth.PI) * 0.9f * sp;
        if (armR != null) armR.xRot = Mth.cos(p) * 0.9f * sp;
    }

    /** Slow breathing sway. */
    static void breathe(ModelPart part, float age, float amount) {
        part.xRot += Mth.sin(age * 0.07f) * 0.03f * amount;
    }

    /** A 0..1..0 swing curve from a 0..1 progress. */
    static float arc(float p) {
        return Mth.sin(Mth.clamp(p, 0f, 1f) * Mth.PI);
    }
}
