package com.astralfall.item;

import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.util.FX;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/**
 * Forged from Astraeus' heart. Every hit stores eclipse energy; at full charge, right-click to
 * unleash an Eclipse Nova that scorches everything around you. Hits burning enemies harder.
 */
public class EclipseGreatswordItem extends Item {
    public static final int MAX_CHARGE = 12;

    public EclipseGreatswordItem(Properties props) {
        super(props);
    }

    public static int charge(ItemStack stack) {
        return ItemUtil.getInt(stack, "eclipse");
    }

    @Override
    public void postHurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        super.postHurtEnemy(stack, target, attacker);
        int c = charge(stack);
        if (c < MAX_CHARGE) ItemUtil.setInt(stack, "eclipse", c + 1);
        target.igniteForSeconds(3);
        if (target.level() instanceof ServerLevel server) {
            FX.burst(server, ParticleTypes.FLAME, target.getBoundingBox().getCenter(), 10, 0.3, 0.05);
            if (c + 1 == MAX_CHARGE) server.playSound(null, attacker.getX(), attacker.getY(), attacker.getZ(), ModSounds.STAR_CHIME.get(), SoundSource.PLAYERS, 1.5f, 0.6f);
        }
    }

    @Override
    public float getAttackDamageBonus(Entity target, float damage, DamageSource source) {
        return target.isOnFire() ? damage * 0.25f : 0.0f;
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (charge(stack) < MAX_CHARGE) {
            if (!level.isClientSide()) player.sendOverlayMessage(Component.translatable("message.astralfall.eclipse.not_ready", charge(stack), MAX_CHARGE).withStyle(ChatFormatting.GOLD));
            return InteractionResult.PASS;
        }
        if (level instanceof ServerLevel server) {
            nova(server, player);
            ItemUtil.setInt(stack, "eclipse", 0);
            stack.hurtAndBreak(5, player, hand);
        }
        player.swing(hand, true);
        return InteractionResult.SUCCESS;
    }

    private void nova(ServerLevel level, Player player) {
        Vec3 c = player.position().add(0, 1, 0);
        level.playSound(null, c.x, c.y, c.z, ModSounds.ECLIPSE_NOVA.get(), SoundSource.PLAYERS, 3.0f, 1.0f);
        FX.burst(level, ParticleTypes.EXPLOSION_EMITTER, c, 1, 0, 0);
        FX.sphere(level, new DustParticleOptions(0x120a18, 3.0f), c.add(0, 3, 0), 1.6, 80);
        FX.sphere(level, ParticleTypes.FLAME, c.add(0, 3, 0), 2.2, 120);
        for (int r = 2; r <= 10; r += 2) {
            FX.ring(level, ParticleTypes.FLAME, c.add(0, -0.8, 0), r, r * 10, 0.05);
            FX.ring(level, ParticleTypes.SOUL_FIRE_FLAME, c.add(0, -0.6, 0), r - 1, r * 6, 0.1);
        }
        FX.burst(level, ModParticles.GOLD_SPARKLE.get(), c, 120, 5.0, 0.2);
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, player.getBoundingBox().inflate(10), e -> e != player && e.isAlive() && !e.isAlliedTo(player))) {
            if (e instanceof net.minecraft.world.entity.TamableAnimal pet && pet.isOwnedBy(player)) continue;
            if (e instanceof Player && !ItemUtil.isHostileTo(e, player)) continue;
            Vec3 away = e.position().subtract(player.position()).multiply(1, 0, 1);
            e.hurtServer(level, level.damageSources().playerAttack(player), 20.0f);
            e.igniteForSeconds(8);
            e.setDeltaMovement(away.normalize().scale(1.2).add(0, 0.7, 0));
            e.hurtMarked = true;
        }
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return charge(stack) >= MAX_CHARGE;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        ItemUtil.tooltip(out, "item.astralfall.eclipse_greatsword.desc", 3);
        int c = charge(stack);
        out.accept(Component.translatable("item.astralfall.eclipse_greatsword.charge", "█".repeat(c) + "░".repeat(MAX_CHARGE - c)).withStyle(c >= MAX_CHARGE ? ChatFormatting.GOLD : ChatFormatting.DARK_GRAY));
    }
}
