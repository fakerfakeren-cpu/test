package com.astralfall.client;

import com.astralfall.entity.boss.AstraeusEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;

import java.util.Random;

/** Client-only camera effects: screen shake from impacts and the eclipse tint near Astraeus. */
public final class ClientFX {
    private static final Random RANDOM = new Random();
    private static float shake;
    private static float eclipse;
    private static AstraeusEntity nearestBoss;

    private ClientFX() {}

    public static void shakeFrom(Vec3 source, float intensity, double range) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null) return;
        double d = mc.player.position().distanceTo(source);
        if (d >= range) return;
        shake = Math.max(shake, intensity * (float) (1.0 - d / range));
    }

    static void onClientTick(TickEvent.ClientTickEvent.Post event) {
        shake *= 0.86f;
        if (shake < 0.02f) shake = 0f;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.player == null) {
            nearestBoss = null;
            eclipse = 0;
            return;
        }
        if (mc.player.tickCount % 10 == 0) {
            nearestBoss = null;
            double best = 80 * 80;
            for (Entity e : mc.level.entitiesForRendering()) {
                if (e instanceof AstraeusEntity boss && boss.isAlive()) {
                    double d = boss.distanceToSqr(mc.player);
                    if (d < best) {
                        best = d;
                        nearestBoss = boss;
                    }
                }
            }
        }
        float want = 0f;
        if (nearestBoss != null && !nearestBoss.isRemoved()) {
            double d = Math.sqrt(nearestBoss.distanceToSqr(mc.player));
            want = (float) Math.max(0, 1 - d / 80) * (nearestBoss.getPhase() >= 2 ? 1.0f : 0.6f);
        }
        eclipse += (want - eclipse) * 0.05f;
    }

    static void onCameraAngles(ViewportEvent.ComputeCameraAngles event) {
        if (shake <= 0f) return;
        float s = Math.min(shake, 8f);
        event.setYaw(event.getYaw() + (RANDOM.nextFloat() - 0.5f) * s);
        event.setPitch(event.getPitch() + (RANDOM.nextFloat() - 0.5f) * s);
        event.setRoll(event.getRoll() + (RANDOM.nextFloat() - 0.5f) * s * 0.6f);
    }

    static void onFogColor(ViewportEvent.ComputeFogColor event) {
        if (eclipse <= 0.01f) return;
        float t = Math.min(0.85f, eclipse);
        event.setRed(event.getRed() + (0.16f - event.getRed()) * t);
        event.setGreen(event.getGreen() + (0.03f - event.getGreen()) * t);
        event.setBlue(event.getBlue() + (0.26f - event.getBlue()) * t);
    }
}
