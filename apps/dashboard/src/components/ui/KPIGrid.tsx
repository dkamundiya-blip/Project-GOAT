import React from 'react';
import { KPICard, KPICardProps } from './KPICard';

interface KPIGridProps {
  cards: KPICardProps[];
  columns?: 2 | 3 | 4 | 5;
}

export const KPIGrid: React.FC<KPIGridProps> = ({ cards, columns = 4 }) => {
  const getColClass = () => {
    switch (columns) {
      case 2:
        return 'grid-cols-1 sm:grid-cols-2';
      case 3:
        return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3';
      case 5:
        return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5';
      default:
        return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4';
    }
  };

  return (
    <div className={`grid ${getColClass()} gap-4`}>
      {cards.map((card, idx) => (
        <KPICard key={idx} {...card} />
      ))}
    </div>
  );
};
