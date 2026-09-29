package com.rimeheart.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;

import java.util.function.Consumer;

/** A hearty winter stew: thaws you out instantly and grants a short Regeneration. */
public class HearthfireStewItem extends Item {
    public HearthfireStewItem(Properties props) {
        super(props);
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        if (!level.isClientSide()) {
            entity.setTicksFrozen(0);
            entity.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 160, 0));
        }
        return super.finishUsingItem(stack, level, entity);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        ItemUtil.tooltip(out, getDescriptionId() + ".desc", 1);
    }
}
