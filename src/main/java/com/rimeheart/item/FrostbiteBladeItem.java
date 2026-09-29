package com.rimeheart.item;

import com.rimeheart.frost.Frost;
import com.rimeheart.registry.ModParticles;
import com.rimeheart.registry.ModSounds;
import com.rimeheart.util.FX;
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
 * Every hit chills the target; fully frozen targets take 30% more damage (Shatter).
 * Use: <b>Cold Snap</b> flash-chills every enemy within 4.5 blocks.
 */
public class FrostbiteBladeItem extends Item {
    public FrostbiteBladeItem(Properties props) {
        super(props);
    }

    @Override
    public void postHurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        super.postHurtEnemy(stack, target, attacker);
        Frost.chill(target, 90);
    }

    @Override
    public float getAttackDamageBonus(Entity target, float damage, DamageSource source) {
        return target instanceof LivingEntity l && Frost.isFrozen(l) ? damage * 0.3f : 0.0f;
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        if (level instanceof ServerLevel server) {
            coldSnap(server, player, 4.5, 150, 2.0f);
            player.getCooldowns().addCooldown(stack, 240);
            stack.hurtAndBreak(2, player, hand);
        }
        player.swing(hand, true);
        return InteractionResult.SUCCESS;
    }

    static int coldSnap(ServerLevel level, Player player, double radius, int chill, float damage) {
        Vec3 c = player.position().add(0, 1, 0);
        FX.ring(level, ParticleTypes.SNOWFLAKE, c.add(0, -0.8, 0), radius, 48, 0.02);
        FX.ring(level, ModParticles.FROST_GLINT.get(), c.add(0, -0.6, 0), radius * 0.6, 30, 0.05);
        FX.burst(level, ModParticles.SNOW_PUFF.get(), c, 30, radius * 0.4, 0.02);
        level.playSound(null, c.x, c.y, c.z, ModSounds.COLD_SNAP.get(), SoundSource.PLAYERS, 1.2f, 1.0f);
        int hit = 0;
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, player.getBoundingBox().inflate(radius, 2, radius),
            e -> e != player && e.isAlive() && !e.isAlliedTo(player) && e.distanceToSqr(player) <= radius * radius)) {
            if (e instanceof net.minecraft.world.entity.TamableAnimal pet && pet.isOwnedBy(player)) continue;
            if (e instanceof Player && !ItemUtil.isHostileTo(e, player)) continue;
            if (damage > 0) e.hurtServer(level, level.damageSources().indirectMagic(player, player), damage);
            Frost.chill(e, chill);
            FX.burst(level, ParticleTypes.SNOWFLAKE, e.getBoundingBox().getCenter(), 10, 0.3, 0.05);
            hit++;
        }
        return hit;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        ItemUtil.tooltip(out, getDescriptionId() + ".desc", 3);
    }
}
