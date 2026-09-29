package com.rimeheart.registry;

import com.rimeheart.Rimeheart;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModTabs {
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Rimeheart.MODID);

    public static final RegistryObject<CreativeModeTab> MAIN = TABS.register("main", () -> CreativeModeTab.builder()
        .title(Component.translatable("itemGroup.rimeheart"))
        .icon(() -> new ItemStack(ModItems.FROSTBITE_BLADE.get()))
        .withTabsBefore(CreativeModeTabs.SPAWN_EGGS)
        .displayItems((params, output) -> {
            for (var item : ModItems.ORDER) output.accept(item.get());
        })
        .build());

    private ModTabs() {}
}
