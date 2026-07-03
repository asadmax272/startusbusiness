export default function RouteSeal() {
  return (
    <svg
      viewBox="0 0 560 420"
      className="w-full max-w-md mx-auto"
      aria-hidden="true"
    >
      {/* route line: Dubai -> Cheyenne, WY, stylized as an arc */}
      <path
        d="M 40 340 Q 280 40 520 200"
        fill="none"
        stroke="#4E6E7A"
        strokeWidth="1.5"
        className="route-line"
      />
      <circle cx="40" cy="340" r="4" fill="#9AA3B2" />
      <text x="14" y="368" fill="#9AA3B2" fontFamily="var(--font-mono)" fontSize="11">
        DXB
      </text>
      <circle cx="520" cy="200" r="4" fill="#C9A24B" />
      <text x="466" y="188" fill="#C9A24B" fontFamily="var(--font-mono)" fontSize="11">
        CHEYENNE, WY
      </text>

      {/* seal */}
      <g transform="translate(280,240)" className="seal">
        <circle r="86" fill="none" stroke="#C9A24B" strokeWidth="2" />
        <circle r="74" fill="none" stroke="#C9A24B" strokeWidth="1" strokeDasharray="2 4" />
        <text
          y="-6"
          textAnchor="middle"
          fill="#C9A24B"
          fontFamily="var(--font-display)"
          fontWeight="600"
          fontSize="15"
        >
          CERTIFICATE OF
        </text>
        <text
          y="16"
          textAnchor="middle"
          fill="#C9A24B"
          fontFamily="var(--font-display)"
          fontWeight="700"
          fontSize="18"
          letterSpacing="1"
        >
          FORMATION
        </text>
        <text
          y="40"
          textAnchor="middle"
          fill="#8A6F35"
          fontFamily="var(--font-mono)"
          fontSize="10"
        >
          STATE OF WYOMING
        </text>
      </g>
    </svg>
  );
}
