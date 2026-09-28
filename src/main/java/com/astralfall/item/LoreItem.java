package com.astralfall.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;

import java.util.function.Consumer;

/** Plain item with a descriptive tooltip and optional enchantment glint. */
public class LoreItem extends Item {
    private final int lines;
    private final boolean foil;

    public LoreItem(Properties props, int lines, boolean foil) {
        super(props);
        this.lines = lines;
        this.foil = foil;
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return foil || super.isFoil(stack);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        if (lines > 0) ItemUtil.tooltip(out, getDescriptionId() + ".desc", lines);
    }
}
