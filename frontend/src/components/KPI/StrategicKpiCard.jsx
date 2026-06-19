export default function StrategicKpiCard({
    title,
    value,
    suffix=""
}) {

    return (
        <div className="bg-white shadow rounded-xl p-5">

            <div className="text-gray-500 text-sm">
                {title}
            </div>

            <div className="text-3xl font-bold mt-2">
                {value}
                {suffix}
            </div>

        </div>
    );
}