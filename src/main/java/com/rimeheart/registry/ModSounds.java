package com.rimeheart.registry;

import com.rimeheart.Rimeheart;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, Rimeheart.MODID);

    public static final RegistryObject<SoundEvent> FREEZE = reg("freeze");
    public static final RegistryObject<SoundEvent> ICE_SHATTER = reg("ice_shatter");
    public static final RegistryObject<SoundEvent> COLD_SNAP = reg("cold_snap");
    public static final RegistryObject<SoundEvent> GLACIER_SLAM = reg("glacier_slam");
    public static final RegistryObject<SoundEvent> BLIZZARD = reg("blizzard");
    public static final RegistryObject<SoundEvent> ICICLE_SHOOT = reg("icicle_shoot");
    public static final RegistryObject<SoundEvent> WRAITH_AMBIENT = reg("wraith_ambient");
    public static final RegistryObject<SoundEvent> WRAITH_HURT = reg("wraith_hurt");
    public static final RegistryObject<SoundEvent> WRAITH_DEATH = reg("wraith_death");
    public static final RegistryObject<SoundEvent> SHARDLING_CHITTER = reg("shardling_chitter");
    public static final RegistryObject<SoundEvent> WINTER_HORN = reg("winter_horn");
    public static final RegistryObject<SoundEvent> SOVEREIGN_ROAR = reg("sovereign_roar");
    public static final RegistryObject<SoundEvent> SOVEREIGN_DEATH = reg("sovereign_death");

    private static RegistryObject<SoundEvent> reg(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(Identifier.fromNamespaceAndPath(Rimeheart.MODID, name)));
    }

    private ModSounds() {}
}
