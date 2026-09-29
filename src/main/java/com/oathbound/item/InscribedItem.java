package com.oathbound.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;

import java.util.function.Consumer;

/** An item whose tooltip carries an inscription (flavour + mechanics lines); relics can shimmer. */
public class InscribedItem extends Item {
    private final int lines;
    private final boolean shimmer;

    public InscribedItem(Properties props, int lines, boolean shimmer) {
        super(props);
        this.lines = lines;
        this.shimmer = shimmer;
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return shimmer || super.isFoil(stack);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        if (lines > 0) Inscriptions.add(out, getDescriptionId() + ".desc", lines);
    }
}
