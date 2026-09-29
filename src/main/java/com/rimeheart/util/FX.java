package com.rimeheart.util;

import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/** Server-side particle helpers. Everything is sent with the "force" flag so effects read from far away. */
public final class FX {
    private FX() {}

    public static void burst(ServerLevel level, ParticleOptions p, Vec3 at, int count, double spread, double speed) {
        level.sendParticles(p, true, true, at.x, at.y, at.z, count, spread, spread, spread, speed);
    }

    public static void burst(ServerLevel level, ParticleOptions p, double x, double y, double z, int count, double sx, double sy, double sz, double speed) {
        level.sendParticles(p, true, true, x, y, z, count, sx, sy, sz, speed);
    }

    public static void line(ServerLevel level, ParticleOptions p, Vec3 from, Vec3 to, double step) {
        Vec3 d = to.subtract(from);
        double len = d.length();
        if (len < 1.0E-4) return;
        Vec3 n = d.scale(1.0 / len);
        for (double t = 0; t <= len; t += step) {
            level.sendParticles(p, true, true, from.x + n.x * t, from.y + n.y * t, from.z + n.z * t, 1, 0, 0, 0, 0);
        }
    }

    public static void ring(ServerLevel level, ParticleOptions p, Vec3 center, double radius, int points, double upSpeed) {
        for (int i = 0; i < points; i++) {
            double a = (Math.PI * 2 * i) / points;
            double x = center.x + Math.cos(a) * radius;
            double z = center.z + Math.sin(a) * radius;
            level.sendParticles(p, true, true, x, center.y, z, 0, Math.cos(a) * 0.1, upSpeed, Math.sin(a) * 0.1, 1.0);
        }
    }

    public static void sphere(ServerLevel level, ParticleOptions p, Vec3 center, double radius, int points) {
        double golden = Math.PI * (3 - Math.sqrt(5));
        for (int i = 0; i < points; i++) {
            double y = 1 - (i / (double) (points - 1)) * 2;
            double r = Math.sqrt(1 - y * y);
            double theta = golden * i;
            level.sendParticles(p, true, true, center.x + Math.cos(theta) * r * radius, center.y + y * radius, center.z + Math.sin(theta) * r * radius, 1, 0, 0, 0, 0);
        }
    }

    /** Particles that spiral inward towards the centre (count = particles per call). */
    public static void spiralIn(ServerLevel level, ParticleOptions p, Vec3 center, double radius, int count, float time) {
        for (int i = 0; i < count; i++) {
            double a = time * 0.35 + (Math.PI * 2 * i) / count;
            double r = radius * (0.4 + 0.6 * ((i * 37 % 100) / 100.0));
            double x = center.x + Math.cos(a) * r;
            double z = center.z + Math.sin(a) * r;
            double y = center.y + Mth.sin(time * 0.2f + i) * 0.6;
            Vec3 v = new Vec3(center.x - x, center.y - y, center.z - z).normalize().scale(0.35);
            level.sendParticles(p, true, true, x, y, z, 0, v.x, v.y, v.z, 1.0);
        }
    }
}
