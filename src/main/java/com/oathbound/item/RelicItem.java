package com.oathbound.item;

import com.oathbound.entity.SpellMarkEntity;
import com.oathbound.event.GameEvents;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.registry.ModTags;
import com.oathbound.util.Vfx;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.EntityTypeTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Relics of the Lanternguard: each holds one old working of the Order, spent with a gesture and slow to return.
 */
public class RelicItem extends InscribedItem {
    public enum Kind {
        /** Bell of the Drowned: a tolling wave that hurls back and reveals everything hostile nearby. */
        BELL(600),
        /** Veyl's Mirror: step through the glass to where you are looking, up to eight blocks. */
        MIRROR(240),
        /** Barrow Censer: grave-smoke that knits wounds and hardens skin, for you and your companions. */
        CENSER(900),
        /** Lanternguard Signet: the Order's call to arms, strength and speed for everyone near. */
        SIGNET(1200),
        /** Heart of the Gloam: the dusk wraps you; what hunted you forgets you. */
        HEART(1200),
        /** Sunshard Talisman: a flash of the first dawn that burns the Gloam and the dead. */
        SUNSHARD(800),
        /** Huntsman's Horn: every hostile thing within thirty-two blocks is outlined in light. */
        HORN(600),
        /** Grove King's Crown: roots burst up under nearby foes and hold them, and the grove mends its bearer. */
        GROVE(700),
        /** Bog Mother's Lantern: snuff it to step ten blocks ahead, leaving blinding marsh-gas behind. */
        MIRE(360),
        /** Cinder Heart: the ground erupts under every foe around; fire cannot touch its bearer for a while. */
        CINDER(900);

        final int cooldown;

        Kind(int cooldown) {
            this.cooldown = cooldown;
        }
    }

    private final Kind kind;

    public RelicItem(Properties props, Kind kind) {
        super(props, 2, false);
        this.kind = kind;
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        if (level instanceof ServerLevel server) {
            if (!invoke(server, player)) return InteractionResult.FAIL;
        }
        player.getCooldowns().addCooldown(stack, GameEvents.cooldown(player, kind.cooldown));
        return InteractionResult.SUCCESS;
    }

    private static void sound(ServerLevel level, Player p, SoundEvent s, float volume, float pitch) {
        level.playSound(null, p.getX(), p.getY(), p.getZ(), s, SoundSource.PLAYERS, volume, pitch);
    }

    private static boolean hostile(LivingEntity e) {
        return e instanceof Enemy || e.typeHolder().is(ModTags.GLOAM_CREATURES);
    }

    private boolean invoke(ServerLevel level, Player p) {
        Vec3 at = p.position();
        switch (kind) {
            case BELL -> {
                sound(level, p, ModSounds.BELL_2.get(), 3.0f, 0.6f);
                sound(level, p, ModSounds.UNDERTOW.get(), 1.2f, 1.3f);
                for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(p.blockPosition()).inflate(7), e -> e != p && hostile(e))) {
                    Vec3 push = e.position().subtract(at).normalize().scale(1.5).add(0, 0.45, 0);
                    e.setDeltaMovement(push);
                    e.hurtMarked = true;
                    e.addEffect(new MobEffectInstance(MobEffects.GLOWING, 200, 0));
                    Vfx.burst(level, ModParticles.TIDE.get(), e.getBoundingBox().getCenter(), 12, 0.3, 0.1);
                }
                SpellMarkEntity.ring(level, at, 9f, SpellMarkEntity.Hue.TIDE, 22);
                SpellMarkEntity.sigil(level, at, 2.4f, SpellMarkEntity.Hue.TIDE, 40);
                Vfx.ring(level, ModParticles.TIDE.get(), at.add(0, 0.3, 0), 3.5, 48, 0.08);
            }
            case MIRROR -> {
                Vec3 look = p.getLookAngle().multiply(1, 0, 1);
                if (look.lengthSqr() < 1e-4) return false;
                look = look.normalize();
                Vec3 dest = null;
                for (double d = 8; d >= 1.5; d -= 0.5) {
                    Vec3 c = at.add(look.scale(d));
                    if (level.noCollision(p, p.getBoundingBox().move(c.subtract(at)))) {
                        dest = c;
                        break;
                    }
                }
                if (dest == null) return false;
                SpellMarkEntity.halo(level, at.add(0, 1.0, 0), 1.2f, SpellMarkEntity.Hue.ARCANE, 20);
                SpellMarkEntity.beam(level, at.add(0, 1.0, 0), dest.add(0, 1.0, 0), 0.3f, SpellMarkEntity.Hue.ARCANE, 10);
                Vfx.burst(level, ModParticles.ARCANE_GLYPH.get(), at.add(0, 1, 0), 24, 0.4, 0.08);
                p.teleportTo(dest.x, dest.y, dest.z);
                p.resetFallDistance();
                Vfx.burst(level, ModParticles.ARCANE_GLYPH.get(), dest.add(0, 1, 0), 24, 0.4, 0.08);
                SpellMarkEntity.halo(level, dest.add(0, 1.0, 0), 1.2f, SpellMarkEntity.Hue.ARCANE, 20);
                sound(level, p, ModSounds.VEYL_BLINK.get(), 1.0f, 1.2f);
            }
            case CENSER -> {
                for (Player q : level.getEntitiesOfClass(Player.class, new AABB(p.blockPosition()).inflate(8))) {
                    q.heal(6f);
                    q.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, 200, 0));
                    Vfx.column(level, ModParticles.SPIRIT.get(), q.position(), 2.4, 24);
                }
                SpellMarkEntity.pillar(level, at, 1.0f, SpellMarkEntity.Hue.SPIRIT, 30);
                SpellMarkEntity.ring(level, at, 8f, SpellMarkEntity.Hue.SPIRIT, 20);
                sound(level, p, ModSounds.HOUSECARL_RISE.get(), 1.2f, 1.4f);
            }
            case SIGNET -> {
                for (Player q : level.getEntitiesOfClass(Player.class, new AABB(p.blockPosition()).inflate(8))) {
                    q.addEffect(new MobEffectInstance(MobEffects.STRENGTH, 400, 0));
                    q.addEffect(new MobEffectInstance(MobEffects.SPEED, 400, 0));
                    Vfx.burst(level, ModParticles.EMBER.get(), q.position().add(0, 1, 0), 20, 0.4, 0.06);
                }
                SpellMarkEntity.sigil(level, at, 3.0f, SpellMarkEntity.Hue.DAWN, 50);
                SpellMarkEntity.halo(level, at.add(0, 2.4, 0), 0.8f, SpellMarkEntity.Hue.DAWN, 50);
                sound(level, p, ModSounds.WAYSHRINE_KINDLE.get(), 1.4f, 1.1f);
            }
            case HEART -> {
                p.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, 240, 0));
                p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 400, 0));
                for (Mob m : level.getEntitiesOfClass(Mob.class, new AABB(p.blockPosition()).inflate(16), m -> m.getTarget() == p)) {
                    m.setTarget(null);
                }
                SpellMarkEntity.pillar(level, at, 1.2f, SpellMarkEntity.Hue.GLOAM, 30);
                Vfx.column(level, ModParticles.GLOAM_WISP.get(), at, 2.6, 60);
                sound(level, p, ModSounds.LANTERN_SNUFF.get(), 1.2f, 0.7f);
            }
            case SUNSHARD -> {
                for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(p.blockPosition()).inflate(8), e -> e != p && hostile(e))) {
                    boolean dark = e.typeHolder().is(EntityTypeTags.UNDEAD) || e.typeHolder().is(ModTags.GLOAM_CREATURES);
                    e.hurtServer(level, level.damageSources().indirectMagic(p, p), dark ? 12f : 6f);
                    if (dark) e.igniteForSeconds(4);
                    Vfx.line(level, ModParticles.SUNBURST.get(), at.add(0, 1.2, 0), e.getBoundingBox().getCenter(), 0.5);
                }
                SpellMarkEntity.ring(level, at, 10f, SpellMarkEntity.Hue.DAWN, 20);
                SpellMarkEntity.pillar(level, at, 1.6f, SpellMarkEntity.Hue.DAWN, 24);
                Vfx.sphere(level, ModParticles.SUNBURST.get(), at.add(0, 1.2, 0), 3, 80);
                sound(level, p, ModSounds.DAWN_BURST.get(), 1.6f, 1.2f);
            }
            case HORN -> {
                int n = 0;
                for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(p.blockPosition()).inflate(32), e -> e != p && hostile(e))) {
                    e.addEffect(new MobEffectInstance(MobEffects.GLOWING, 300, 0));
                    n++;
                }
                SpellMarkEntity.ring(level, at, 14f, SpellMarkEntity.Hue.SPIRIT, 26);
                sound(level, p, ModSounds.WARHORN.get(), 2.5f, 1.5f);
                p.sendOverlayMessage(net.minecraft.network.chat.Component.translatable("message.oathbound.horn", n));
            }
            case GROVE -> {
                for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(p.blockPosition()).inflate(8), e -> e != p && hostile(e))) {
                    e.hurtServer(level, level.damageSources().thorns(p), 5f);
                    e.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 100, 5));
                    e.setDeltaMovement(0, 0.35, 0);
                    e.hurtMarked = true;
                    SpellMarkEntity.sigil(level, e.position(), 1.1f, SpellMarkEntity.Hue.GROVE, 30);
                    SpellMarkEntity.pillar(level, e.position(), 0.6f, SpellMarkEntity.Hue.GROVE, 14);
                    Vfx.burst(level, new net.minecraft.core.particles.BlockParticleOption(net.minecraft.core.particles.ParticleTypes.BLOCK,
                        net.minecraft.world.level.block.Blocks.ROOTED_DIRT.defaultBlockState()), e.position().add(0, 0.4, 0), 24, 0.4, 0.2);
                }
                for (Player q : level.getEntitiesOfClass(Player.class, new AABB(p.blockPosition()).inflate(8))) {
                    q.heal(4f);
                    q.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 120, 0));
                }
                SpellMarkEntity.sigil(level, at, 3.5f, SpellMarkEntity.Hue.GROVE, 40);
                SpellMarkEntity.ring(level, at, 9f, SpellMarkEntity.Hue.GROVE, 22);
                Vfx.ring(level, ModParticles.PETAL.get(), at.add(0, 0.4, 0), 4, 60, 0.1);
                sound(level, p, ModSounds.ELDERHORN_BELLOW.get(), 1.0f, 1.6f);
                sound(level, p, net.minecraft.sounds.SoundEvents.ROOTED_DIRT_BREAK, 2.0f, 0.6f);
            }
            case MIRE -> {
                Vec3 look = p.getLookAngle().multiply(1, 0, 1);
                if (look.lengthSqr() < 1e-4) return false;
                look = look.normalize();
                Vec3 dest = null;
                for (double d = 10; d >= 2; d -= 0.5) {
                    Vec3 c = at.add(look.scale(d));
                    if (level.noCollision(p, p.getBoundingBox().move(c.subtract(at)))) {
                        dest = c;
                        break;
                    }
                }
                if (dest == null) {
                    p.sendOverlayMessage(net.minecraft.network.chat.Component.translatable("message.oathbound.relic.no_room"));
                    return false;
                }
                var cloud = new net.minecraft.world.entity.AreaEffectCloud(level, at.x, at.y, at.z);
                cloud.setOwner(p);
                cloud.setRadius(3.0f);
                cloud.setDuration(100);
                cloud.setRadiusPerTick(-0.01f);
                cloud.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 1));
                cloud.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 60, 0));
                level.addFreshEntity(cloud);
                for (Mob m : level.getEntitiesOfClass(Mob.class, new AABB(p.blockPosition()).inflate(16), m -> m.getTarget() == p)) {
                    m.setTarget(null);
                }
                Vfx.burst(level, ModParticles.SPORE.get(), at.add(0, 1, 0), 40, 0.6, 0.06);
                SpellMarkEntity.beam(level, at.add(0, 1.0, 0), dest.add(0, 1.0, 0), 0.25f, SpellMarkEntity.Hue.MIRE, 10);
                p.teleportTo(dest.x, dest.y, dest.z);
                p.resetFallDistance();
                Vfx.burst(level, ModParticles.SPORE.get(), dest.add(0, 1, 0), 24, 0.4, 0.06);
                SpellMarkEntity.sigil(level, dest, 1.3f, SpellMarkEntity.Hue.MIRE, 20);
                sound(level, p, ModSounds.HAG_CACKLE.get(), 0.8f, 1.5f);
                sound(level, p, ModSounds.LANTERN_SNUFF.get(), 1.0f, 1.2f);
            }
            case CINDER -> {
                p.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 600, 0));
                p.clearFire();
                for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(p.blockPosition()).inflate(10), e -> e != p && hostile(e))) {
                    e.hurtServer(level, level.damageSources().indirectMagic(p, p), 8f);
                    e.igniteForSeconds(6);
                    e.setDeltaMovement(e.getDeltaMovement().x, 0.8, e.getDeltaMovement().z);
                    e.hurtMarked = true;
                    SpellMarkEntity.pillar(level, e.position(), 0.9f, SpellMarkEntity.Hue.EMBER, 16);
                    Vfx.column(level, net.minecraft.core.particles.ParticleTypes.FLAME, e.position(), 4, 30);
                }
                SpellMarkEntity.sigil(level, at, 3.0f, SpellMarkEntity.Hue.EMBER, 40);
                SpellMarkEntity.ring(level, at, 11f, SpellMarkEntity.Hue.EMBER, 22);
                SpellMarkEntity.halo(level, at.add(0, 1.2, 0), 0.9f, SpellMarkEntity.Hue.EMBER, 40);
                Vfx.ring(level, ModParticles.EMBER.get(), at.add(0, 0.3, 0), 3.5, 60, 0.12);
                sound(level, p, ModSounds.COLOSSUS_ROAR.get(), 0.9f, 1.4f);
                sound(level, p, net.minecraft.sounds.SoundEvents.BLAZE_SHOOT, 1.5f, 0.7f);
            }
        }
        return true;
    }
}
