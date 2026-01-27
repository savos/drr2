import { motion } from 'framer-motion';

/**
 * Base Skeleton component for loading states
 * Provides shimmer animation effect for better UX
 */
export function Skeleton({ className = '', variant = 'rectangle', width, height }) {
  const baseClasses = 'bg-gradient-to-r from-zinc-200 via-zinc-300 to-zinc-200 dark:from-zinc-800 dark:via-zinc-700 dark:to-zinc-800';
  const variantClasses = variant === 'circle' ? 'rounded-full' : 'rounded-lg';

  const style = {};
  if (width) style.width = width;
  if (height) style.height = height;

  return (
    <motion.div
      className={`${baseClasses} ${variantClasses} ${className}`}
      style={{
        ...style,
        backgroundSize: '200% 100%',
      }}
      animate={{
        backgroundPosition: ['0% 0%', '100% 0%'],
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: 'linear',
      }}
    />
  );
}

/**
 * Pre-built skeleton for integration cards
 */
export function SkeletonCard() {
  return (
    <div className="integration-card">
      <div className="integration-header">
        <div className="flex items-center gap-3 flex-1">
          <Skeleton variant="circle" className="w-10 h-10" />
          <div className="flex-1">
            <Skeleton className="h-5 w-3/4 mb-2" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        </div>
      </div>
      <div className="integration-meta">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
      </div>
      <div className="integration-actions">
        <Skeleton className="h-10 w-24" />
        <Skeleton className="h-10 w-24" />
      </div>
    </div>
  );
}

/**
 * Skeleton for stat cards on dashboard
 */
export function SkeletonStatCard() {
  return (
    <div className="stat-card">
      <Skeleton variant="circle" className="w-12 h-12" />
      <div className="flex-1">
        <Skeleton className="h-6 w-16 mb-2" />
        <Skeleton className="h-4 w-24" />
      </div>
    </div>
  );
}

/**
 * Skeleton for action cards
 */
export function SkeletonActionCard() {
  return (
    <div className="action-card">
      <Skeleton variant="circle" className="w-10 h-10 mb-2" />
      <Skeleton className="h-4 w-20" />
    </div>
  );
}

/**
 * Skeleton for table rows
 */
export function SkeletonTableRow({ columns = 3 }) {
  return (
    <div className="flex items-center gap-4 p-4 border-b border-zinc-200 dark:border-zinc-700">
      {Array.from({ length: columns }).map((_, index) => (
        <Skeleton key={index} className="h-4 flex-1" />
      ))}
    </div>
  );
}

/**
 * Skeleton for text blocks (paragraphs)
 */
export function SkeletonText({ lines = 3 }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          className="h-4"
          width={index === lines - 1 ? '80%' : '100%'}
        />
      ))}
    </div>
  );
}
