// src/types/vis-timeline.d.ts
declare module 'vis-timeline' {
    export class Timeline {
        constructor(container: HTMLElement, items: any[], options: any);
        setItems(items: any[]): void;
        setOptions(options: any): void;
        destroy(): void;
        redraw(): void;
        fit(): void;
        moveTo(time: number): void;
        setSelection(ids: number[]): void;
        getSelection(): number[];
        on(event: string, callback: (props: any) => void): void;
        off(event: string): void;
    }
    export class DataSet {
        constructor(data?: any[], options?: any);
        add(data: any): void;
        update(data: any): void;
        remove(id: any): void;
        get(): any[];
        getDataSet(): any;
    }
}