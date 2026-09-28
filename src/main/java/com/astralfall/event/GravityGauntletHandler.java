package com.astralfall.event;

import com.astralfall.entity.boss.AstraeusEntity;
import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.util.FX;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.item.FallingBlockEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;

/** Server-side state for the Gravity Gauntlet: which entity each player holds and what is in flight. */
public final class GravityGauntletHandler {
    private record Thrown(UUID thrower, net.minecraft.resources.ResourceKey<net.minecraft.world.level.Level> dim, int[] ticks) {}

    private static final Map<UUID, Integer> HELD = new HashMap<>();
    private static final Map<Integer, Thrown> THROWN = new HashMap<>();

    private GravityGauntletHandler() {}

    private static boolean canGrab(Entity e, Player player) {
        if (e == player || !e.isAlive() || e.isSpectator() || e instanceof AstraeusEntity) return false;
        if (e instanceof Player p && (p.isCreative() || p.isSpectator())) return false;
        if (e instanceof LivingEntity living) return living.getMaxHealth() <= 150 && e.getBbWidth() < 3.0f;
        return e instanceof ItemEntity || e instanceof FallingBlockEntity;
    }

    public static boolean tryGrab(ServerLevel level, Player player) {
        Vec3 eye = player.getEyePosition();
        Vec3 look = player.getLookAngle();
        Vec3 end = eye.add(look.scale(16));
        AABB box = player.getBoundingBox().expandTowards(look.scale(16)).inflate(1.0);
        EntityHitResult hit = ProjectileUtil.getEntityHitResult(player, eye, end, box, e -> canGrab(e, player), 16 * 16);
        Entity grabbed = hit != null ? hit.getEntity() : null;
        if (grabbed == null && player.isShiftKeyDown()) {
            BlockHitResult bhr = level.clip(new ClipContext(eye, eye.add(look.scale(7)), ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, player));
            if (bhr.getType() == HitResult.Type.BLOCK) {
                BlockPos pos = bhr.getBlockPos();
                BlockState state = level.getBlockState(pos);
                float hardness = state.getDestroySpeed(level, pos);
                if (!state.isAir() && !state.hasBlockEntity() && hardness >= 0 && hardness < 20 && state.getFluidState().isEmpty()
                    && player.mayInteract(level, pos)) {
                    FallingBlockEntity fb = FallingBlockEntity.fall(level, pos, state);
                    fb.setHurtsEntities(2.0f, 40);
                    grabbed = fb;
                }
            }
        }
        if (grabbed == null) {
            player.sendOverlayMessage(Component.translatable("message.astralfall.gauntlet.nothing").withStyle(ChatFormatting.GRAY));
            return false;
        }
        HELD.put(player.getUUID(), grabbed.getId());
        level.playSound(null, grabbed.getX(), grabbed.getY(), grabbed.getZ(), ModSounds.GRAVITY_GRAB.get(), SoundSource.PLAYERS, 1.2f, 1.0f);
        FX.burst(level, ParticleTypes.REVERSE_PORTAL, grabbed.getBoundingBox().getCenter(), 30, 0.4, 0.2);
        return true;
    }

    private static Entity held(Player player) {
        Integer id = HELD.get(player.getUUID());
        if (id == null) return null;
        Entity e = player.level().getEntity(id);
        if (e == null || !e.isAlive() || e.distanceToSqr(player) > 24 * 24) {
            HELD.remove(player.getUUID());
            return null;
        }
        return e;
    }

    public static boolean hold(Player player) {
        Entity e = held(player);
        if (e == null) return false;
        Vec3 anchor = player.getEyePosition().add(player.getLookAngle().scale(3.5 + e.getBbWidth())).subtract(0, e.getBbHeight() * 0.5, 0);
        Vec3 delta = anchor.subtract(e.position());
        e.setDeltaMovement(delta.scale(0.45));
        e.hurtMarked = true;
        e.resetFallDistance();
        if (e instanceof FallingBlockEntity fb) fb.time = 1;
        if (e instanceof Mob mob) mob.getNavigation().stop();
        if (player.level() instanceof ServerLevel level && player.tickCount % 2 == 0) {
            Vec3 hand = player.getEyePosition().add(player.getLookAngle().scale(0.8)).add(0, -0.4, 0);
            FX.line(level, ModParticles.VOID_MOTE.get(), hand, e.getBoundingBox().getCenter(), 0.7);
            FX.ring(level, ParticleTypes.REVERSE_PORTAL, e.position(), Math.max(0.6, e.getBbWidth()), 10, 0.05);
        }
        return true;
    }

    public static boolean throwHeld(Player player) {
        Entity e = held(player);
        HELD.remove(player.getUUID());
        if (e == null) return false;
        e.setDeltaMovement(player.getLookAngle().scale(2.6).add(0, 0.15, 0));
        e.hurtMarked = true;
        THROWN.put(e.getId(), new Thrown(player.getUUID(), player.level().dimension(), new int[]{0}));
        if (player.level() instanceof ServerLevel level) {
            level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.GRAVITY_THROW.get(), SoundSource.PLAYERS, 1.2f, 1.0f);
            FX.burst(level, ModParticles.VOID_MOTE.get(), e.getBoundingBox().getCenter(), 20, 0.3, 0.3);
        }
        return true;
    }

    public static void onPlayerTick(Player player) {
        if (HELD.containsKey(player.getUUID()) && !player.isUsingItem()) HELD.remove(player.getUUID());
    }

    public static void tick(ServerLevel level) {
        if (THROWN.isEmpty()) return;
        Iterator<Map.Entry<Integer, Thrown>> it = THROWN.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<Integer, Thrown> entry = it.next();
            if (entry.getValue().dim() != level.dimension()) continue;
            Entity e = level.getEntity(entry.getKey());
            if (e == null) {
                it.remove();
                continue;
            }
            int t = ++entry.getValue().ticks()[0];
            Entity thrower = level.getEntity(entry.getValue().thrower());
            boolean impact = false;
            LivingEntity victim = null;
            if (t > 2) {
                for (LivingEntity other : level.getEntitiesOfClass(LivingEntity.class, e.getBoundingBox().inflate(0.6), o -> o != e && o != thrower && o.isAlive())) {
                    victim = other;
                    impact = true;
                    break;
                }
                if (e.horizontalCollision || e.verticalCollision || e.onGround()) impact = true;
            }
            if (impact) {
                var src = thrower instanceof Player p ? level.damageSources().playerAttack(p) : level.damageSources().flyIntoWall();
                if (e instanceof LivingEntity living) living.hurtServer(level, src, 8.0f);
                if (victim != null) {
                    victim.hurtServer(level, src, 8.0f);
                    victim.setDeltaMovement(e.getDeltaMovement().scale(0.6).add(0, 0.3, 0));
                    victim.hurtMarked = true;
                }
                FX.burst(level, ParticleTypes.EXPLOSION, e.position(), 2, 0.3, 0);
                FX.burst(level, ModParticles.VOID_MOTE.get(), e.position(), 25, 0.5, 0.2);
                level.playSound(null, e.getX(), e.getY(), e.getZ(), ModSounds.SHOCKWAVE.get(), SoundSource.PLAYERS, 1.0f, 1.5f);
                it.remove();
            } else if (t > 80) {
                it.remove();
            }
        }
    }
}
