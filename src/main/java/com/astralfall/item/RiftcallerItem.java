package com.astralfall.item;

import com.astralfall.entity.SingularityEntity;
import com.astralfall.registry.ModItems;
import com.astralfall.registry.ModParticles;
import com.astralfall.util.FX;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/** Void scythe. Right-click tears open a black hole where you aim. Every hit siphons life. */
public class RiftcallerItem extends Item {
    public RiftcallerItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        if (level instanceof ServerLevel server) {
            Vec3 at = ItemUtil.lookTarget(player, 24);
            Vec3 back = at.subtract(player.getEyePosition()).normalize();
            at = at.subtract(back).add(0, 1.0, 0);
            SingularityEntity.spawn(server, at, player, 90, 8.0f, 14.0f, false);
            FX.line(server, ModParticles.VOID_MOTE.get(), player.getEyePosition().add(0, -0.3, 0), at, 0.5);
            player.getCooldowns().addCooldown(stack, 200);
            stack.hurtAndBreak(3, player, hand);
        }
        player.swing(hand, true);
        return InteractionResult.SUCCESS;
    }

    @Override
    public void postHurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        super.postHurtEnemy(stack, target, attacker);
        attacker.heal(2.0f);
        if (target.level() instanceof ServerLevel server) {
            FX.line(server, ModParticles.VOID_MOTE.get(), target.getBoundingBox().getCenter(), attacker.position().add(0, 1, 0), 0.4);
            if (!target.isAlive() && target instanceof net.minecraft.world.entity.monster.Enemy && server.getRandom().nextInt(8) == 0) {
                target.spawnAtLocation(server, new ItemStack(ModItems.VOID_ESSENCE.get()));
            }
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        ItemUtil.tooltip(out, "item.astralfall.riftcaller.desc", 3);
    }
}
