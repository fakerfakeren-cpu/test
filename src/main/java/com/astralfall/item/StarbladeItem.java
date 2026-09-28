package com.astralfall.item;

import com.astralfall.entity.projectile.StarSlashEntity;
import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.registry.ModTags;
import com.astralfall.util.FX;
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
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/**
 * Right-click: fire a piercing crescent of starlight. Sneak + right-click: Starlight Dash, blinking
 * forward through enemies. Deals +50% damage to void creatures.
 */
public class StarbladeItem extends Item {
    public StarbladeItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        if (level instanceof ServerLevel server) {
            if (player.isShiftKeyDown()) {
                dash(server, player);
                player.getCooldowns().addCooldown(stack, 50);
            } else {
                server.addFreshEntity(StarSlashEntity.create(server, player));
                server.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.STAR_SLASH.get(), SoundSource.PLAYERS, 1.0f, 0.9f + player.getRandom().nextFloat() * 0.2f);
                player.getCooldowns().addCooldown(stack, 22);
            }
            stack.hurtAndBreak(1, player, hand);
        }
        player.swing(hand, true);
        return InteractionResult.SUCCESS;
    }

    private void dash(ServerLevel level, Player player) {
        Vec3 look = player.getLookAngle().multiply(1, 0.2, 1).normalize();
        Vec3 start = player.position();
        Vec3 end = start.add(look.scale(8));
        AABB path = new AABB(start, end).inflate(1.3, 1.0, 1.3);
        for (Entity e : level.getEntities(player, path, e -> e instanceof LivingEntity && e.isAlive() && !e.isAlliedTo(player))) {
            float dmg = 8.0f;
            if (e.typeHolder().is(ModTags.VOID_CREATURES)) dmg *= 1.5f;
            e.hurtServer(level, level.damageSources().playerAttack(player), dmg);
            FX.burst(level, ModParticles.STAR_SPARKLE.get(), e.getBoundingBox().getCenter(), 12, 0.3, 0.1);
        }
        player.setDeltaMovement(look.x * 2.4, 0.25, look.z * 2.4);
        player.hurtMarked = true;
        player.resetFallDistance();
        FX.line(level, ModParticles.STAR_SPARKLE.get(), start.add(0, 1, 0), end.add(0, 1, 0), 0.3);
        FX.line(level, ParticleTypes.END_ROD, start.add(0, 0.5, 0), end.add(0, 0.5, 0), 0.8);
        level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.VOID_BLINK.get(), SoundSource.PLAYERS, 1.0f, 1.5f);
    }

    @Override
    public float getAttackDamageBonus(Entity target, float damage, DamageSource source) {
        return target.typeHolder().is(ModTags.VOID_CREATURES) ? damage * 0.5f : 0.0f;
    }

    @Override
    public void postHurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        super.postHurtEnemy(stack, target, attacker);
        if (target.level() instanceof ServerLevel server) {
            FX.burst(server, ModParticles.STAR_SPARKLE.get(), target.getBoundingBox().getCenter(), 8, 0.3, 0.1);
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        ItemUtil.tooltip(out, "item.astralfall.starblade.desc", 3);
    }
}
