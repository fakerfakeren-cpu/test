package com.astralfall.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SimpleAnimatedParticle;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.core.particles.SimpleParticleType;

/** Glowing animated particle used for every Astralfall particle type. */
public class AstralParticle extends SimpleAnimatedParticle {
    protected AstralParticle(ClientLevel level, double x, double y, double z, double dx, double dy, double dz,
                             SpriteSet sprites, int color, int fade, float gravity, int life, float size) {
        super(level, x, y, z, sprites, gravity);
        this.xd = dx;
        this.yd = dy;
        this.zd = dz;
        this.lifetime = life + this.random.nextInt(Math.max(1, life / 2));
        this.quadSize *= size;
        this.friction = 0.9f;
        setColor(color);
        setFadeColor(fade);
        setSpriteFromAge(sprites);
    }

    public static ParticleProvider<SimpleParticleType> provider(SpriteSet sprites, int color, int fade, float gravity, int life, float size) {
        return (type, level, x, y, z, dx, dy, dz, random) -> new AstralParticle(level, x, y, z, dx, dy, dz, sprites, color, fade, gravity, life, size);
    }
}
