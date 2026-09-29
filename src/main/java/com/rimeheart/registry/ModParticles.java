package com.rimeheart.registry;

import com.rimeheart.Rimeheart;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModParticles {
    public static final DeferredRegister<ParticleType<?>> PARTICLES = DeferredRegister.create(ForgeRegistries.PARTICLE_TYPES, Rimeheart.MODID);

    /** Glinting ice crystal (pale cyan). */
    public static final RegistryObject<SimpleParticleType> FROST_GLINT = PARTICLES.register("frost_glint", () -> new SimpleParticleType(true));
    /** Drifting powdery snow puff. */
    public static final RegistryObject<SimpleParticleType> SNOW_PUFF = PARTICLES.register("snow_puff", () -> new SimpleParticleType(true));
    /** Ghostly teal wisp shed by Frost Wraiths and Wraithweave. */
    public static final RegistryObject<SimpleParticleType> WRAITH_WISP = PARTICLES.register("wraith_wisp", () -> new SimpleParticleType(true));

    private ModParticles() {}
}
