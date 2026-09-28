package com.astralfall.item;

import com.astralfall.event.Starfall;
import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.util.FX;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemUseAnimation;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/**
 * Hold right-click to call a meteor down on whatever you are looking at. Sneak + right-click for a
 * Ground Slam that launches everything around you.
 */
public class CometMaulItem extends Item {
    public CometMaulItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        if (player.isShiftKeyDown()) {
            if (level instanceof ServerLevel server) {
                slam(server, player);
                player.getCooldowns().addCooldown(stack, 60);
                stack.hurtAndBreak(2, player, hand);
            }
            player.swing(hand, true);
            return InteractionResult.SUCCESS;
        }
        player.startUsingItem(hand);
        return InteractionResult.CONSUME;
    }

    @Override
    public void onUseTick(Level level, LivingEntity entity, ItemStack stack, int remaining) {
        if (level instanceof ServerLevel server && entity instanceof Player player) {
            int used = getUseDuration(stack, entity) - remaining;
            Vec3 target = ItemUtil.lookTarget(player, 48);
            if (used % 2 == 0) FX.ring(server, ModParticles.COMET_TRAIL.get(), target.add(0, 0.2, 0), Math.max(0.5, 3.0 - used * 0.1), 12, 0.02);
            if (used == 20) server.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.STAR_CHIME.get(), SoundSource.PLAYERS, 1.0f, 0.7f);
        }
    }

    @Override
    public boolean releaseUsing(ItemStack stack, Level level, LivingEntity entity, int remaining) {
        if (!(entity instanceof Player player)) return false;
        int used = getUseDuration(stack, entity) - remaining;
        if (used < 20) return false;
        if (level instanceof ServerLevel server) {
            Vec3 target = ItemUtil.lookTarget(player, 48);
            Starfall.spawnMeteor(server, BlockPos.containing(target), Starfall.Variant.SMALL, 1.2f);
            player.getCooldowns().addCooldown(stack, 100);
            stack.hurtAndBreak(3, player, player.getUsedItemHand());
        }
        return true;
    }

    private void slam(ServerLevel level, Player player) {
        Vec3 c = player.position();
        BlockState ground = level.getBlockState(player.blockPosition().below());
        level.playSound(null, c.x, c.y, c.z, ModSounds.SHOCKWAVE.get(), SoundSource.PLAYERS, 2.0f, 1.1f);
        for (int ring = 1; ring <= 4; ring++) {
            FX.ring(level, ParticleTypes.EXPLOSION, c.add(0, 0.2, 0), ring * 1.5, ring * 4, 0);
            if (!ground.isAir()) FX.ring(level, new BlockParticleOption(ParticleTypes.BLOCK, ground), c.add(0, 0.3, 0), ring * 1.5, ring * 14, 0.3);
        }
        FX.ring(level, ModParticles.COMET_TRAIL.get(), c.add(0, 0.2, 0), 6, 48, 0.05);
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, player.getBoundingBox().inflate(6.5, 2, 6.5), e -> e != player && e.isAlive() && !e.isAlliedTo(player))) {
            if (e instanceof net.minecraft.world.entity.TamableAnimal pet && pet.isOwnedBy(player)) continue;
            Vec3 away = e.position().subtract(c).multiply(1, 0, 1);
            double d = Math.max(1, away.length());
            e.hurtServer(level, level.damageSources().playerAttack(player), (float) (12.0 - d));
            e.setDeltaMovement(away.normalize().scale(0.9).add(0, 0.85, 0));
            e.hurtMarked = true;
        }
    }

    @Override
    public int getUseDuration(ItemStack stack, LivingEntity entity) {
        return 72000;
    }

    @Override
    public ItemUseAnimation getUseAnimation(ItemStack stack) {
        return ItemUseAnimation.SPEAR;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        ItemUtil.tooltip(out, "item.astralfall.comet_maul.desc", 3);
    }
}
