package com.oathbound.client;

import com.oathbound.entity.boss.KeeperEntity;
import com.oathbound.entity.boss.MorvaneEntity;
import com.oathbound.registry.ModWorldgen;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;

import java.util.Random;

/**
 * Client camera mood: boss moves shake the view, the Gloaming's fog breathes violet, and the Hollow King
 * drains colour from the world around him.
 */
public final class Atmosphere {
    private static final Random RANDOM = new Random();
    private static float shake;
    private static float dusk;
    private static KeeperEntity nearest;

    private Atmosphere() {}

    public static void shake(float intensity) {
        shake = Math.max(shake, intensity);
    }

    static void onClientTick(TickEvent.ClientTickEvent.Post event) {
        shake *= 0.85f;
        if (shake < 0.02f) shake = 0f;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.player == null) {
            nearest = null;
            dusk = 0;
            return;
        }
        if (mc.player.tickCount % 10 == 0) {
            nearest = null;
            double best = 48 * 48;
            for (Entity e : mc.level.entitiesForRendering()) {
                if (e instanceof KeeperEntity k && k.isAlive() && !k.isSleeping()) {
                    double d = k.distanceToSqr(mc.player);
                    if (d < best) {
                        best = d;
                        nearest = k;
                    }
                }
            }
        }
        float want = mc.level.dimension() == ModWorldgen.GLOAMING ? 0.55f : 0f;
        if (nearest != null && !nearest.isRemoved()) {
            if (nearest.move() != KeeperEntity.IDLE && nearest.moveTicks() % 6 == 0) shake(nearest instanceof MorvaneEntity ? 1.2f : 0.6f);
            if (nearest instanceof MorvaneEntity m) want = m.isHollow() ? 0.95f : Math.max(want, 0.7f);
        }
        dusk += (want - dusk) * 0.04f;
    }

    static void onCameraAngles(ViewportEvent.ComputeCameraAngles event) {
        if (shake <= 0f) return;
        float s = Math.min(shake, 6f);
        event.setYaw(event.getYaw() + (RANDOM.nextFloat() - 0.5f) * s);
        event.setPitch(event.getPitch() + (RANDOM.nextFloat() - 0.5f) * s);
        event.setRoll(event.getRoll() + (RANDOM.nextFloat() - 0.5f) * s * 0.5f);
    }

    static void onFogColor(ViewportEvent.ComputeFogColor event) {
        if (dusk <= 0.01f) return;
        float t = Math.min(0.9f, dusk);
        float pulse = (float) Math.sin(System.currentTimeMillis() / 2200.0) * 0.03f;
        event.setRed(event.getRed() + (0.19f + pulse - event.getRed()) * t);
        event.setGreen(event.getGreen() + (0.10f - event.getGreen()) * t);
        event.setBlue(event.getBlue() + (0.27f + pulse - event.getBlue()) * t);
    }
}
