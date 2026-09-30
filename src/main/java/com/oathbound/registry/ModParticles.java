package com.oathbound.registry;

import com.oathbound.Oathbound;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModParticles {
    public static final DeferredRegister<ParticleType<?>> PARTICLES = DeferredRegister.create(ForgeRegistries.PARTICLE_TYPES, Oathbound.MODID);

    /** Warm rising spark from lanterns, braziers and the Everflame. */
    public static final RegistryObject<SimpleParticleType> EMBER = reg("ember");
    /** Soft pale-gold mote of lumenite light. */
    public static final RegistryObject<SimpleParticleType> LUMEN_MOTE = reg("lumen_mote");
    /** Drifting violet-black smoke of the Gloam. */
    public static final RegistryObject<SimpleParticleType> GLOAM_WISP = reg("gloam_wisp");
    /** Blue-violet arcane rune (Veyl, the Spire, the Staff). */
    public static final RegistryObject<SimpleParticleType> ARCANE_GLYPH = reg("arcane_glyph");
    /** Spectral teal wisp (wights, housecarls, oath tethers). */
    public static final RegistryObject<SimpleParticleType> SPIRIT = reg("spirit");
    /** Bright white-gold flare of the dawn. */
    public static final RegistryObject<SimpleParticleType> SUNBURST = reg("sunburst");
    /** Sea-green drowned glimmer (Caldris, the chapel). */
    public static final RegistryObject<SimpleParticleType> TIDE = reg("tide");
    /** A tumbling spring-green petal (the Elderhorn, groves). */
    public static final RegistryObject<SimpleParticleType> PETAL = reg("petal");
    /** A drifting marsh-light spore (the Bog Mother, swamps). */
    public static final RegistryObject<SimpleParticleType> SPORE = reg("spore");
    /** A blinking firefly of warm summer nights. */
    public static final RegistryObject<SimpleParticleType> FIREFLY = reg("firefly");
    /** A grey-orange flake of falling ash (the Cinder Colossus, burnt lands). */
    public static final RegistryObject<SimpleParticleType> ASH = reg("ash");

    private static RegistryObject<SimpleParticleType> reg(String name) {
        return PARTICLES.register(name, () -> new SimpleParticleType(true));
    }

    private ModParticles() {}
}
