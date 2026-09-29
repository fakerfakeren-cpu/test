package com.oathbound.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SimpleAnimatedParticle;
import net.minecraft.client.particle.SingleQuadParticle;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.Mth;

/**
 * The single particle class behind every Oathbound particle type. Each type is a "recipe": colours that
 * blend from birth to death, a size curve that swells then shrinks, gentle drag, optional lift or fall, and
 * a slow spin. Rendered at full brightness so it reads as light in dark places.
 */
public class GlimmerParticle extends SimpleAnimatedParticle {
    public record Recipe(int birth, int death, float lift, int life, float size, float spin, float drag) {}

    private final SpriteSet sprites;
    private final Recipe recipe;
    private final float baseSize;
    private final float spinSpeed;

    protected GlimmerParticle(ClientLevel level, double x, double y, double z, double dx, double dy, double dz, SpriteSet sprites, Recipe r) {
        super(level, x, y, z, sprites, -r.lift());
        this.sprites = sprites;
        this.recipe = r;
        this.xd = dx;
        this.yd = dy;
        this.zd = dz;
        this.lifetime = r.life() + random.nextInt(Math.max(1, r.life() / 2));
        this.baseSize = quadSize * r.size() * (0.75f + random.nextFloat() * 0.5f);
        this.quadSize = baseSize * 0.3f;
        this.friction = r.drag();
        this.spinSpeed = (random.nextFloat() - 0.5f) * r.spin();
        this.roll = random.nextFloat() * Mth.TWO_PI;
        setColor(r.birth());
        setFadeColor(r.death());
        setSpriteFromAge(sprites);
    }

    @Override
    public void tick() {
        super.tick();
        float t = age / (float) Math.max(1, lifetime);
        // swell quickly, linger, then shrink away
        float curve = t < 0.15f ? t / 0.15f : 1.0f - Math.max(0, (t - 0.6f) / 0.4f);
        this.quadSize = baseSize * (0.3f + 0.7f * curve);
        this.oRoll = this.roll;
        this.roll += spinSpeed;
    }

    @Override
    public SingleQuadParticle.Layer getLayer() {
        return SingleQuadParticle.Layer.TRANSLUCENT;
    }

    public static ParticleProvider<SimpleParticleType> provider(SpriteSet sprites, Recipe recipe) {
        return (type, level, x, y, z, dx, dy, dz, random) -> new GlimmerParticle(level, x, y, z, dx, dy, dz, sprites, recipe);
    }
}
