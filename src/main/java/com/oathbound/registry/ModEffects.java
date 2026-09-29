package com.oathbound.registry;

import com.oathbound.Oathbound;
import com.oathbound.event.OathEffects;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.effect.MobEffect;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModEffects {
    public static final DeferredRegister<MobEffect> EFFECTS = DeferredRegister.create(ForgeRegistries.MOB_EFFECTS, Oathbound.MODID);

    public static final RegistryObject<MobEffect> RADIANCE = EFFECTS.register("radiance", OathEffects.Radiance::new);
    public static final RegistryObject<MobEffect> GLOAMROT = EFFECTS.register("gloamrot", OathEffects.Gloamrot::new);
    public static final RegistryObject<MobEffect> SUNMARK = EFFECTS.register("sunmark", OathEffects.Sunmark::new);

    public static Holder<MobEffect> holder(RegistryObject<MobEffect> effect) {
        return BuiltInRegistries.MOB_EFFECT.wrapAsHolder(effect.get());
    }

    private ModEffects() {}
}
