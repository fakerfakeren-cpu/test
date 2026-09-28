package com.astralfall.registry;

import com.astralfall.Astralfall;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModTabs {
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Astralfall.MODID);

    public static final RegistryObject<CreativeModeTab> MAIN = TABS.register("main", () -> CreativeModeTab.builder()
        .title(Component.translatable("itemGroup.astralfall"))
        .icon(() -> new ItemStack(ModItems.STARBLADE.get()))
        .withTabsBefore(CreativeModeTabs.SPAWN_EGGS)
        .displayItems((params, output) -> {
            for (var item : ModItems.ORDER) output.accept(item.get());
        })
        .build());

    private ModTabs() {}
}
