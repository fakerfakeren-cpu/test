package com.oathbound.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.Mth;

/** A firefly: it wanders in lazy loops and blinks, slowly, on and off. */
public class FireflyParticle extends GlimmerParticle {
    private final float phase = random.nextFloat() * Mth.TWO_PI;
    private final float rate = 0.12f + random.nextFloat() * 0.1f;

    protected FireflyParticle(ClientLevel level, double x, double y, double z, double dx, double dy, double dz, SpriteSet sprites, Recipe r) {
        super(level, x, y, z, dx, dy, dz, sprites, r);
        this.lifetime = 90 + random.nextInt(80);
    }

    @Override
    public void tick() {
        super.tick();
        // lazy loops
        this.xd += (random.nextFloat() - 0.5f) * 0.004f;
        this.yd += (random.nextFloat() - 0.5f) * 0.003f;
        this.zd += (random.nextFloat() - 0.5f) * 0.004f;
        // a slow blink: long glow, short dark
        float b = Mth.sin(age * rate + phase);
        float glow = Mth.clamp(b * 1.6f + 0.4f, 0f, 1f);
        float fade = Math.min(1f, Math.min(age / 10f, (lifetime - age) / 20f));
        setAlpha(glow * fade);
    }

    public static ParticleProvider<SimpleParticleType> provider(SpriteSet sprites, Recipe recipe) {
        return (type, level, x, y, z, dx, dy, dz, random) -> new FireflyParticle(level, x, y, z, dx, dy, dz, sprites, recipe);
    }
}
