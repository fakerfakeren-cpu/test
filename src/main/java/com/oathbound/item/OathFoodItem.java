package com.oathbound.item;

import com.oathbound.registry.ModEffects;
import com.oathbound.registry.ModParticles;
import com.oathbound.util.Vfx;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;

import java.util.function.Consumer;

/** Food and drink with an effect on top: honeyed mead, a knight's stew and the Elixir of Dawn. */
public class OathFoodItem extends Item {
    public enum Kind { MEAD, STEW, ELIXIR }

    private final Kind kind;

    public OathFoodItem(Properties props, Kind kind) {
        super(props);
        this.kind = kind;
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        if (level instanceof ServerLevel server) {
            switch (kind) {
                case MEAD -> {
                    entity.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 200, 0));
                    entity.addEffect(new MobEffectInstance(MobEffects.ABSORPTION, 1200, 0));
                    entity.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 60, 0));
                }
                case STEW -> {
                    entity.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, 1800, 0));
                    entity.addEffect(new MobEffectInstance(MobEffects.STRENGTH, 600, 0));
                }
                case ELIXIR -> {
                    entity.removeEffect(ModEffects.holder(ModEffects.GLOAMROT));
                    entity.removeEffect(MobEffects.DARKNESS);
                    entity.removeEffect(MobEffects.BLINDNESS);
                    entity.addEffect(new MobEffectInstance(ModEffects.holder(ModEffects.RADIANCE), 3600, 0));
                    Vfx.burst(server, ModParticles.SUNBURST.get(), entity.position().add(0, 1, 0), 40, 0.5, 0.1);
                }
            }
        }
        return super.finishUsingItem(stack, level, entity);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        Inscriptions.add(out, getDescriptionId() + ".desc", 1);
    }
}
