package com.oathbound.item;

import com.oathbound.event.GameEvents;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

/**
 * The Staff of Veyl. Its Arcane Chain strikes the creature you aim at, then leaps from foe to foe, up to five,
 * weakening a little with every jump. Cooldown is halved by the full Arcanist regalia.
 */
public class StaffOfVeylItem extends Item {
    public static final int MAX_TARGETS = 5;

    public StaffOfVeylItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        if (level instanceof ServerLevel server) {
            Vec3 eye = player.getEyePosition();
            Vec3 look = player.getLookAngle();
            LivingEntity first = null;
            double best = 0.93;
            for (LivingEntity e : server.getEntitiesOfClass(LivingEntity.class, player.getBoundingBox().inflate(20), e -> valid(e, player))) {
                Vec3 to = e.getBoundingBox().getCenter().subtract(eye);
                double d = to.length();
                if (d > 20) continue;
                double dot = to.normalize().dot(look) + (1 - d / 20) * 0.02;
                if (dot > best && player.hasLineOfSight(e)) {
                    best = dot;
                    first = e;
                }
            }
            server.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.ARCANE_CHAIN.get(), SoundSource.PLAYERS, 1.2f, 1.0f);
            Vec3 tip = eye.add(look.scale(0.8)).add(0, -0.25, 0);
            if (first == null) {
                Vec3 end = eye.add(look.scale(16));
                var hit = server.clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
                if (hit.getType() != HitResult.Type.MISS) end = hit.getLocation();
                arc(server, tip, end);
                Vfx.burst(server, ModParticles.ARCANE_GLYPH.get(), end, 10, 0.2, 0.05);
            } else {
                List<LivingEntity> hit = new ArrayList<>();
                LivingEntity cur = first;
                Vec3 from = tip;
                float dmg = 8.0f;
                while (cur != null && hit.size() < MAX_TARGETS) {
                    hit.add(cur);
                    Vec3 c = cur.getBoundingBox().getCenter();
                    arc(server, from, c);
                    cur.hurtServer(server, server.damageSources().indirectMagic(player, player), dmg);
                    Vfx.burst(server, ParticleTypes.ELECTRIC_SPARK, c, 12, 0.3, 0.2);
                    Vfx.burst(server, ModParticles.ARCANE_GLYPH.get(), c, 8, 0.3, 0.05);
                    dmg *= 0.82f;
                    from = c;
                    LivingEntity next = null;
                    double nd = 8 * 8;
                    for (LivingEntity e : server.getEntitiesOfClass(LivingEntity.class, cur.getBoundingBox().inflate(8), e -> valid(e, player) && !hit.contains(e))) {
                        double d = e.distanceToSqr(cur);
                        if (d < nd) {
                            nd = d;
                            next = e;
                        }
                    }
                    cur = next;
                }
            }
            stack.hurtAndBreak(1, player, hand);
        }
        player.getCooldowns().addCooldown(stack, GameEvents.cooldown(player, 24));
        return InteractionResult.SUCCESS;
    }

    private static boolean valid(LivingEntity e, Player player) {
        if (e == player || !e.isAlive() || e.isSpectator()) return false;
        if (e instanceof TamableAnimal pet && pet.isOwnedBy(player)) return false;
        if (e instanceof com.oathbound.entity.mob.SpectralHousecarlEntity h && h.isAlly()) return false;
        if (e instanceof Player p) return Inscriptions.isFoeOf(p, player);
        return e instanceof net.minecraft.world.entity.monster.Enemy || (e instanceof net.minecraft.world.entity.Mob m && m.getTarget() == player);
    }

    /** A jagged violet lightning arc. */
    public static void arc(ServerLevel level, Vec3 from, Vec3 to) {
        Vec3 d = to.subtract(from);
        int segs = Math.max(3, (int) (d.length() * 1.5));
        var r = level.getRandom();
        Vec3 prev = from;
        for (int i = 1; i <= segs; i++) {
            Vec3 p = from.add(d.scale(i / (double) segs));
            if (i < segs) p = p.add((r.nextDouble() - 0.5) * 0.5, (r.nextDouble() - 0.5) * 0.5, (r.nextDouble() - 0.5) * 0.5);
            Vfx.line(level, ModParticles.ARCANE_GLYPH.get(), prev, p, 0.25);
            prev = p;
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        Inscriptions.add(out, getDescriptionId() + ".desc", 3);
    }
}
