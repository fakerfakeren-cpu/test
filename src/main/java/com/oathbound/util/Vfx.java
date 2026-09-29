package com.oathbound.util;

import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.phys.Vec3;

/**
 * Server-side particle choreography. Every call is sent with long-distance visibility so boss moves and rites
 * read from across an arena.
 */
public final class Vfx {
    private Vfx() {}

    private static void one(ServerLevel level, ParticleOptions p, double x, double y, double z, double vx, double vy, double vz, double speed) {
        // count 0 = the (vx, vy, vz) triple is a velocity rather than a spread
        level.sendParticles(p, true, true, x, y, z, 0, vx, vy, vz, speed);
    }

    /** A random puff: {@code count} particles spread over a cube of half-size {@code spread}. */
    public static void burst(ServerLevel level, ParticleOptions p, Vec3 at, int count, double spread, double speed) {
        level.sendParticles(p, true, true, at.x, at.y, at.z, count, spread, spread, spread, speed);
    }

    /** Particles every {@code step} blocks along a straight segment. */
    public static void line(ServerLevel level, ParticleOptions p, Vec3 a, Vec3 b, double step) {
        Vec3 d = b.subtract(a);
        double len = d.length();
        if (len < 1.0E-3) return;
        int n = Math.max(1, (int) Math.ceil(len / step));
        for (int i = 0; i <= n; i++) {
            Vec3 q = a.add(d.scale(i / (double) n));
            one(level, p, q.x, q.y, q.z, 0, 0, 0, 0);
        }
    }

    /** A flat ring in the XZ plane, drifting outward and upward. */
    public static void ring(ServerLevel level, ParticleOptions p, Vec3 c, double radius, int points, double rise) {
        double phase = level.getRandom().nextDouble() * Math.PI * 2;
        for (int i = 0; i < points; i++) {
            double a = phase + Math.PI * 2 * i / points;
            double cx = Math.cos(a), cz = Math.sin(a);
            one(level, p, c.x + cx * radius, c.y, c.z + cz * radius, cx * 0.08, rise, cz * 0.08, 1.0);
        }
    }

    /** An evenly spaced shell (latitude bands), so large spheres look solid rather than speckled. */
    public static void sphere(ServerLevel level, ParticleOptions p, Vec3 c, double radius, int points) {
        int bands = Math.max(3, (int) Math.sqrt(points / 2.0));
        int placed = 0;
        for (int b = 0; b <= bands && placed < points; b++) {
            double lat = Math.PI * b / bands - Math.PI / 2;
            double r = Math.cos(lat) * radius;
            int around = Math.max(1, (int) Math.round(bands * 2 * Math.cos(lat)));
            for (int i = 0; i < around && placed < points; i++, placed++) {
                double lon = Math.PI * 2 * i / around + b * 0.37;
                one(level, p, c.x + Math.cos(lon) * r, c.y + Math.sin(lat) * radius, c.z + Math.sin(lon) * r, 0, 0, 0, 0);
            }
        }
    }

    /** A rotating vortex of particles sucked towards the centre; call every tick with an increasing {@code time}. */
    public static void spiralIn(ServerLevel level, ParticleOptions p, Vec3 c, double radius, int count, float time) {
        RandomSource r = level.getRandom();
        for (int i = 0; i < count; i++) {
            double a = time * 0.3 + Math.PI * 2 * i / count;
            double rr = radius * (0.5 + 0.5 * r.nextDouble());
            double x = c.x + Math.cos(a) * rr, z = c.z + Math.sin(a) * rr, y = c.y + (r.nextDouble() - 0.5) * 1.2;
            Vec3 v = new Vec3(c.x - x, c.y - y, c.z - z).normalize();
            // tangential swirl + inward pull
            one(level, p, x, y, z, v.x * 0.3 - Math.sin(a) * 0.1, v.y * 0.3, v.z * 0.3 + Math.cos(a) * 0.1, 1.0);
        }
    }

    /** A vertical column of rising particles (braziers, pillars, lanterns). */
    public static void column(ServerLevel level, ParticleOptions p, Vec3 base, double height, int count) {
        RandomSource r = level.getRandom();
        for (int i = 0; i < count; i++) {
            one(level, p, base.x + (r.nextDouble() - 0.5) * 0.6, base.y + r.nextDouble() * height, base.z + (r.nextDouble() - 0.5) * 0.6, 0, 0.05, 0, 1.0);
        }
    }
}
