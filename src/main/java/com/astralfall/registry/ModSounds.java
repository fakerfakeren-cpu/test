package com.astralfall.registry;

import com.astralfall.Astralfall;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, Astralfall.MODID);

    public static final RegistryObject<SoundEvent> METEOR_INCOMING = reg("meteor_incoming");
    public static final RegistryObject<SoundEvent> METEOR_IMPACT = reg("meteor_impact");
    public static final RegistryObject<SoundEvent> STAR_CHIME = reg("star_chime");
    public static final RegistryObject<SoundEvent> STARSTORM = reg("starstorm");
    public static final RegistryObject<SoundEvent> WISP_AMBIENT = reg("wisp_ambient");
    public static final RegistryObject<SoundEvent> WISP_HURT = reg("wisp_hurt");
    public static final RegistryObject<SoundEvent> STALKER_AMBIENT = reg("stalker_ambient");
    public static final RegistryObject<SoundEvent> STALKER_SCREAM = reg("stalker_scream");
    public static final RegistryObject<SoundEvent> STALKER_BLINK = reg("stalker_blink");
    public static final RegistryObject<SoundEvent> CRAWLER_ROLL = reg("crawler_roll");
    public static final RegistryObject<SoundEvent> CRAWLER_HURT = reg("crawler_hurt");
    public static final RegistryObject<SoundEvent> GAZER_CHARGE = reg("gazer_charge");
    public static final RegistryObject<SoundEvent> GAZER_BEAM = reg("gazer_beam");
    public static final RegistryObject<SoundEvent> BOSS_ROAR = reg("boss_roar");
    public static final RegistryObject<SoundEvent> BOSS_SUMMON = reg("boss_summon");
    public static final RegistryObject<SoundEvent> BOSS_BEAM = reg("boss_beam");
    public static final RegistryObject<SoundEvent> BOSS_DEATH = reg("boss_death");
    public static final RegistryObject<SoundEvent> SHOCKWAVE = reg("shockwave");
    public static final RegistryObject<SoundEvent> SINGULARITY_HUM = reg("singularity_hum");
    public static final RegistryObject<SoundEvent> SINGULARITY_COLLAPSE = reg("singularity_collapse");
    public static final RegistryObject<SoundEvent> STAR_SLASH = reg("star_slash");
    public static final RegistryObject<SoundEvent> STAR_BOLT = reg("star_bolt");
    public static final RegistryObject<SoundEvent> GRAVITY_GRAB = reg("gravity_grab");
    public static final RegistryObject<SoundEvent> GRAVITY_THROW = reg("gravity_throw");
    public static final RegistryObject<SoundEvent> VOID_BLINK = reg("void_blink");
    public static final RegistryObject<SoundEvent> ECLIPSE_NOVA = reg("eclipse_nova");
    public static final RegistryObject<SoundEvent> VAULT_OPEN = reg("vault_open");

    private static RegistryObject<SoundEvent> reg(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(Identifier.fromNamespaceAndPath(Astralfall.MODID, name)));
    }

    private ModSounds() {}
}
