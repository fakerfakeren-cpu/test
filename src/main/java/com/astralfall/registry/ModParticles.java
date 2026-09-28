package com.astralfall.registry;

import com.astralfall.Astralfall;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModParticles {
    public static final DeferredRegister<ParticleType<?>> PARTICLES = DeferredRegister.create(ForgeRegistries.PARTICLE_TYPES, Astralfall.MODID);

    /** Four-point twinkling star (cyan/white). */
    public static final RegistryObject<SimpleParticleType> STAR_SPARKLE = PARTICLES.register("star_sparkle", () -> new SimpleParticleType(true));
    /** Golden star used by the Fallen Star, Crown and Wisps. */
    public static final RegistryObject<SimpleParticleType> GOLD_SPARKLE = PARTICLES.register("gold_sparkle", () -> new SimpleParticleType(true));
    /** Dark violet mote drawn into singularities and void creatures. */
    public static final RegistryObject<SimpleParticleType> VOID_MOTE = PARTICLES.register("void_mote", () -> new SimpleParticleType(true));
    /** Hot comet trail left by meteors. */
    public static final RegistryObject<SimpleParticleType> COMET_TRAIL = PARTICLES.register("comet_trail", () -> new SimpleParticleType(true));

    private ModParticles() {}
}
