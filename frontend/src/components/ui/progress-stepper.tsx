import { CheckCircle2, Circle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Step {
    id: string;
    label: string;
    status: 'pending' | 'inprogress' | 'completed';
}

interface ProgressStepperProps {
    steps: Step[];
    className?: string;
}

export function ProgressStepper({ steps, className }: ProgressStepperProps) {
    return (
        <div className={cn('space-y-4', className)}>
            {steps.map((step, index) => (
                <div key={step.id} className="flex items-center gap-4">
                    <div className="relative flex items-center justify-center">
                        {step.status === 'completed' && (
                            <CheckCircle2 className="h-6 w-6 text-green-500" />
                        )}
                        {step.status === 'inprogress' && (
                            <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
                        )}
                        {step.status === 'pending' && (
                            <Circle className="h-6 w-6 text-gray-300" />
                        )}

                        {/* Connecting Line (except for last item) */}
                        {index < steps.length - 1 && (
                            <div className={cn(
                                "absolute left-1/2 top-6 h-full w-0.5 -translate-x-1/2",
                                step.status === 'completed' ? "bg-green-500" : "bg-gray-200"
                            )} style={{ height: '16px' }} />
                        )}
                    </div>
                    <span className={cn(
                        "text-sm font-medium transition-colors duration-300",
                        step.status === 'completed' ? "text-gray-900" :
                            step.status === 'inprogress' ? "text-blue-600" : "text-gray-400"
                    )}>
                        {step.label}
                    </span>
                </div>
            ))}
        </div>
    );
}
