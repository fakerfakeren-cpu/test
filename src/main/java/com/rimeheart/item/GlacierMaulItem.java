package com.rimeheart.item;

import com.rimeheart.frost.Frost;
import com.rimeheart.registry.ModParticles;
import com.rimeheart.registry.ModSounds;
import com.rimeheart.util.FX;
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
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/** Heavy and slow. Use: <b>Permafrost Slam</b>, a ring of ice spikes that launches and freezes nearby enemies. */
public class GlacierMaulItem extends Item {
    public GlacierMaulItem(Properties props) {
        super(props);
    }

    @Override
    public void postHurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        super.postHurtEnemy(stack, target, attacker);
        Frost.chill(target, 60);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(stack) || !player.onGround()) return InteractionResult.PASS;
        if (level instanceof ServerLevel server) {
            slam(server, player);
            player.getCooldowns().addCooldown(stack, 100);
            stack.hurtAndBreak(2, player, hand);
        }
        player.swing(hand, true);
        return InteractionResult.SUCCESS;
    }

    private static void slam(ServerLevel level, Player player) {
        Vec3 c = player.position();
        level.playSound(null, c.x, c.y, c.z, ModSounds.GLACIER_SLAM.get(), SoundSource.PLAYERS, 1.6f, 1.0f);
        var ice = new BlockParticleOption(ParticleTypes.BLOCK, Blocks.PACKED_ICE.defaultBlockState());
        for (int ring = 1; ring <= 5; ring++) {
            FX.ring(level, ice, c.add(0, 0.3, 0), ring, ring * 10, 0.35);
            FX.ring(level, ParticleTypes.SNOWFLAKE, c.add(0, 0.2, 0), ring, ring * 6, 0.1);
        }
        for (int i = 0; i < 12; i++) {
            double a = i * Math.PI / 6;
            Vec3 base = c.add(Math.cos(a) * 3.2, 0, Math.sin(a) * 3.2);
            FX.line(level, ModParticles.FROST_GLINT.get(), base, base.add(0, 1.6 + (i % 3) * 0.5, 0), 0.25);
            FX.burst(level, ice, base.x, base.y + 0.5, base.z, 6, 0.1, 0.5, 0.1, 0.1);
        }
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, player.getBoundingBox().inflate(5, 2, 5), e -> e != player && e.isAlive() && !e.isAlliedTo(player))) {
            if (e instanceof net.minecraft.world.entity.TamableAnimal pet && pet.isOwnedBy(player)) continue;
            if (e instanceof Player && !ItemUtil.isHostileTo(e, player)) continue;
            Vec3 away = e.position().subtract(c).multiply(1, 0, 1);
            double d = Math.max(1, away.length());
            if (d > 5.5) continue;
            e.hurtServer(level, level.damageSources().playerAttack(player), (float) Math.max(3.0, 10.0 - d * 1.2));
            Frost.chill(e, 140);
            e.setDeltaMovement(away.normalize().scale(0.5).add(0, 0.65, 0));
            e.hurtMarked = true;
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        ItemUtil.tooltip(out, getDescriptionId() + ".desc", 3);
    }
}
